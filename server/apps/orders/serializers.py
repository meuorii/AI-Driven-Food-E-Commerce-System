from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
import random
import string
from .models import OrdersOrder, OrdersOrderitem
from apps.products.models import CartItem
from apps.users.models import UsersCustomerAddress, UsersRiderProfile
from apps.products.serializers import ProductsFooditemSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    food_item = ProductsFooditemSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrdersOrderitem
        fields = [
            "id",
            "food_item",
            "quantity",
            "price_at_order",
            "total_price"
        ]

    def get_total_price(self, obj):
        return obj.price_at_order * obj.quantity

class RiderInfoSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = UsersRiderProfile
        fields = ["id", "name", "phone", "plate_number"]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.SerializerMethodField()

    class Meta:
        model = OrdersOrder
        fields = [
            "id",
            "order_code",
            "customer",
            "stall",
            "total_amount",
            "status",
            "payment_method",
            "order_type",
            "delivery_address",
            "cancel_reason",
            "created_at",
            "updated_at",
            "items"
        ]
        read_only_fields = ["created_at", "updated_at", "status", "order_code"]

    def get_customer(self, obj):
        profile = obj.customer
        first = getattr(profile, "first_name", "") or ""
        last = getattr(profile, "last_name", "") or ""
        full_name = f"{first} {last}".strip()
        return {
            "id": profile.user.id,
            "name": full_name or profile.user.email,
            "email": profile.user.email,
            "phone": getattr(profile, "phone", None),
        }


class CheckoutSerializer(serializers.Serializer):
    cart_item = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, write_only=True)
    payment_method = serializers.ChoiceField(choices=OrdersOrder.PAYMENT_METHOD_CHOICES)
    order_type = serializers.ChoiceField(choices=OrdersOrder.ORDER_TYPE_CHOICES)
    address_id = serializers.IntegerField(required=False)

    def generate_order_code(self):
        timestamp = timezone.now().strftime("%y%m%d%H%M%S")
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"ORD{timestamp}{random_part}"

    def validate(self, data):
        request = self.context["request"]
        customer = request.user.customer_profile
        cart_item_ids = data["cart_item"]
        order_type = data["order_type"]
        address_id = data.get("address_id")

        cart_items = CartItem.objects.select_related("food_item", "stall").filter(id__in=cart_item_ids, customer=customer)
        if not cart_items.exists():
            raise serializers.ValidationError("No valid cart items selected.")

        stalls = set(item.stall_id for item in cart_items)
        if len(stalls) > 1:
            raise serializers.ValidationError("All cart items must belong to the same stall.")

        if order_type == "delivery":
            if not address_id:
                raise serializers.ValidationError({"address_id": "Address is required for delivery."})
            if not UsersCustomerAddress.objects.filter(id=address_id, customer=customer).exists():
                raise serializers.ValidationError("Invalid address.")

        data["cart_items"] = cart_items
        return data

    def create(self, validated_data):
        request = self.context["request"]
        customer = request.user.customer_profile
        cart_items = validated_data["cart_items"]
        order_type = validated_data["order_type"]
        payment_method = validated_data["payment_method"]
        address_id = validated_data.get("address_id")
        total_amount = 0
        address_string = None
        stall = cart_items.first().stall

        if order_type == "delivery":
            address = UsersCustomerAddress.objects.get(id=address_id)
            address_string = f"{address.street}, {address.barangay}, {address.city}, {address.province}"

        with transaction.atomic():
            order = OrdersOrder.objects.create(
                order_code=self.generate_order_code(),
                customer=customer,
                stall=stall,
                total_amount=0,
                payment_method=payment_method,
                order_type=order_type,
                delivery_address=address_string
            )

            order_items = []
            for cart in cart_items:
                food = cart.food_item
                if not food.is_active or not food.is_available:
                    raise serializers.ValidationError(f"{food.name} is not available.")
                if food.stock_quantity < cart.quantity:
                    raise serializers.ValidationError(f"Insufficient stock for {food.name}.")

                price = food.price
                total_amount += price * cart.quantity
                order_items.append(
                    OrdersOrderitem(
                        order=order,
                        food_item=food,
                        quantity=cart.quantity,
                        price_at_order=price
                    )
                )

            OrdersOrderitem.objects.bulk_create(order_items)
            order.total_amount = total_amount
            order.save()
            cart_items.delete()

        return order


class VendorOrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    rider = serializers.SerializerMethodField()

    class Meta:
        model = OrdersOrder
        fields = [
            "id",
            "order_code",
            "customer",         # ✅ customer name + info
            "status",
            "total_amount",
            "payment_method",
            "order_type",
            "delivery_address",
            "cancel_reason",
            "rider",            # ✅ assigned rider info (if delivery)
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = ["created_at", "updated_at", "status", "order_code"]

    def get_customer(self, obj):
        profile = obj.customer
        first = getattr(profile, "first_name", "") or ""
        last = getattr(profile, "last_name", "") or ""
        full_name = f"{first} {last}".strip()
        return {
            "id": profile.user.id,
            "name": full_name or profile.user.email,
            "email": profile.user.email,
            "phone": getattr(profile, "phone", None),
        }

    def get_rider(self, obj):
        if not obj.rider:
            return None
        return RiderInfoSerializer(obj.rider).data

    def get_items(self, obj):
        vendor_stall = self.context["request"].user.vendor_profile.vendorsstall_set.first()
        vendor_items = obj.items.filter(food_item__stall=vendor_stall)
        return OrderItemSerializer(vendor_items, many=True).data


class RiderOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.SerializerMethodField()
    rider = serializers.SerializerMethodField()

    class Meta:
        model = OrdersOrder
        fields = [
            "id",
            "order_code",
            "customer",         # ✅ customer name + info
            "stall",
            "status",
            "total_amount",
            "payment_method",
            "order_type",
            "delivery_address", # ✅ important for rider
            "cancel_reason",
            "rider",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = ["created_at", "updated_at", "status", "order_code"]

    def get_customer(self, obj):
        profile = obj.customer
        first = getattr(profile, "first_name", "") or ""
        last = getattr(profile, "last_name", "") or ""
        full_name = f"{first} {last}".strip()
        return {
            "id": profile.user.id,
            "name": full_name or profile.user.email,
            "email": profile.user.email,
            "phone": getattr(profile, "phone", None),
        }

    def get_rider(self, obj):
        if not obj.rider:
            return None
        return RiderInfoSerializer(obj.rider).data

class AvailableRidersSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = UsersRiderProfile
        fields = ["id", "name", "phone", "plate_number"]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()