from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import OrdersOrder
from .serializers import (
    CheckoutSerializer,
    OrderSerializer,
    VendorOrderSerializer,
    RiderOrderSerializer,
    AvailableRidersSerializer
)
from apps.users.models import UsersRiderProfile
from .utils import log_order_activity


def get_customer_name(order):
    profile = order.customer
    first = profile.first_name or ""
    last = profile.last_name or ""
    full_name = f"{first} {last}".strip()
    return full_name or profile.user.email


def order_response(message, order, extra=None):
    data = {
        "message": message,
        "order": {
            "id": order.id,
            "customer": get_customer_name(order),
            "status": order.status,
            "order_type": order.order_type,
        }
    }
    if extra:
        data.update(extra)
    return data


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            order = serializer.save()
            response_data = OrderSerializer(order).data
            return Response(
                {
                    "message": "Order placed successfully",
                    "order": response_data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id=None):
        customer = request.user.customer_profile

        if order_id:
            try:
                order = OrdersOrder.objects.prefetch_related(
                    "items", "items__food_item"
                ).get(id=order_id, customer=customer)
                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except OrdersOrder.DoesNotExist:
                return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        orders = OrdersOrder.objects.filter(
            customer=customer
        ).prefetch_related(
            "items", "items__food_item"
        ).order_by("-created_at")

        serializer = OrderSerializer(orders, many=True)
        return Response({"orders": serializer.data}, status=status.HTTP_200_OK)


class CustomerCancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        customer = request.user.customer_profile
        try:
            order = OrdersOrder.objects.get(id=order_id, customer=customer)
            if order.status != "pending":
                return Response(
                    {"error": f"Order #{order.id} cannot be cancelled. Only pending orders can be cancelled."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.status = "cancelled"
            order.cancelled_by = "customer"
            order.save()
            return Response(
                order_response(f"Order #{order.id} has been successfully cancelled.", order),
                status=status.HTTP_200_OK
            )
        except OrdersOrder.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)


class VendorOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get_vendor_stall(self):
        vendor = self.request.user.vendor_profile
        return vendor.vendorsstall_set.first()

    def get_order(self, order_id):
        vendor_stall = self.get_vendor_stall()
        return OrdersOrder.objects.filter(
            id=order_id,
            stall=vendor_stall
        ).exclude(
            status="cancelled", cancelled_by="customer"
        ).prefetch_related("items", "items__food_item").first()

    def get(self, request, order_id=None, **kwargs):
        vendor_stall = self.get_vendor_stall()
        if order_id:
            order = self.get_order(order_id)
            if not order:
                return Response({"error": "Order not found."}, status=404)
            serializer = VendorOrderSerializer(order, context={"request": request})
            return Response(serializer.data, status=200)

        orders = OrdersOrder.objects.filter(
            stall=vendor_stall
        ).exclude(
            status="cancelled", cancelled_by="customer"
        ).prefetch_related("items", "items__food_item").order_by("-created_at")

        serializer = VendorOrderSerializer(orders, many=True, context={"request": request})
        return Response({"orders": serializer.data}, status=200)

    def post(self, request, order_id, action, **kwargs):
        vendor_stall = self.get_vendor_stall()
        vendor = request.user.vendor_profile
        order = self.get_order(order_id)

        if not order:
            return Response({"error": "Order not found."}, status=404)

        customer_name = get_customer_name(order)

        if action == "confirm":
            if order.status != "pending":
                return Response(
                    {"error": f"Order #{order.id} for {customer_name} cannot be confirmed. Only pending orders can be confirmed."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            for item in order.items.filter(food_item__stall=vendor_stall):
                food_item = item.food_item
                if food_item.stock_quantity < item.quantity:
                    return Response(
                        {"error": f"Not enough stock for '{food_item.name}'. Available: {food_item.stock_quantity}, Requested: {item.quantity}."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                food_item.stock_quantity -= item.quantity
                food_item.save()
            order.status = "confirmed"
            order.save()
            log_order_activity(vendor, "Confirmed order", order=order, stall=vendor_stall)
            return Response(
                order_response(f"Order #{order.id} for {customer_name} has been confirmed.", order),
                status=status.HTTP_200_OK
            )

        elif action == "cancel":
            if order.status not in ["pending", "confirmed"]:
                return Response(
                    {"error": f"Order #{order.id} for {customer_name} cannot be cancelled at this stage."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if order.status == "confirmed":
                for item in order.items.filter(food_item__stall=vendor_stall):
                    food_item = item.food_item
                    food_item.stock_quantity += item.quantity
                    food_item.save()
            reason = request.data.get("reason")
            if not reason:
                return Response({"error": "Cancel reason is required."}, status=status.HTTP_400_BAD_REQUEST)
            order.status = "cancelled"
            order.cancelled_by = "vendor"
            order.cancel_reason = reason
            order.save()
            log_order_activity(vendor, "Cancelled order", order=order, stall=vendor_stall)
            return Response(
                order_response(
                    f"Order #{order.id} for {customer_name} has been cancelled. Reason: {reason}",
                    order
                ),
                status=status.HTTP_200_OK
            )

        elif action == "prepare":
            if order.status != "confirmed":
                return Response(
                    {"error": f"Order #{order.id} for {customer_name} must be confirmed before preparing."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.status = "preparing"
            order.save()
            log_order_activity(vendor, "Preparing order", order=order, stall=vendor_stall)
            return Response(
                order_response(f"Order #{order.id} for {customer_name} is now being prepared.", order),
                status=status.HTTP_200_OK
            )

        elif action == "ready":
            if order.status != "preparing":
                return Response(
                    {"error": f"Order #{order.id} for {customer_name} must be in preparing status before marking as ready."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if order.order_type == "delivery":
                rider_id = request.data.get("rider_id")
                if not rider_id:
                    return Response(
                        {"error": f"Order #{order.id} is a delivery order. Please assign a rider by providing rider_id."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                try:
                    rider = UsersRiderProfile.objects.get(id=rider_id, is_available=True, is_approved=True)
                    order.rider = rider
                    rider_name = f"{rider.first_name} {rider.last_name}".strip()
                except UsersRiderProfile.DoesNotExist:
                    return Response(
                        {"error": "Rider not found or is not available/approved."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            order.status = "ready_for_pickup"
            order.save()
            log_order_activity(vendor, "Ready order", order=order, stall=vendor_stall)

            if order.order_type == "delivery":
                return Response(
                    order_response(
                        f"Order #{order.id} for {customer_name} is ready. Rider {rider_name} has been assigned.",
                        order,
                        extra={"assigned_rider": rider_name}
                    ),
                    status=status.HTTP_200_OK
                )
            return Response(
                order_response(f"Order #{order.id} for {customer_name} is ready for pickup.", order),
                status=status.HTTP_200_OK
            )

        elif action == "complete":
            if order.order_type != "pickup":
                return Response(
                    {"error": f"Order #{order.id} is a delivery order and cannot be completed by the vendor."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if order.status != "ready_for_pickup":
                return Response(
                    {"error": f"Order #{order.id} for {customer_name} must be ready for pickup before completing."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.status = "completed"
            order.save()
            log_order_activity(vendor, "Completed order", order=order, stall=vendor_stall)
            return Response(
                order_response(f"Order #{order.id} for {customer_name} has been completed. Thank you!", order),
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"error": f"Invalid action '{action}'."},
                status=status.HTTP_400_BAD_REQUEST
            )


class AvailableRidersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        riders = UsersRiderProfile.objects.filter(
            is_available=True,
            is_approved=True
        ).select_related("user")

        serializer = AvailableRidersSerializer(riders, many=True)
        return Response({"available_riders": serializer.data}, status=status.HTTP_200_OK)


class RiderOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get_orders(self):
        return OrdersOrder.objects.filter(
            order_type="delivery"
        ).exclude(status="cancelled").prefetch_related("items", "items__food_item")

    def get(self, request, order_id=None, **kwargs):
        rider = getattr(request.user, "rider_profile", None)
        if not rider:
            return Response({"error": "Rider profile not found."}, status=status.HTTP_404_NOT_FOUND)

        if order_id:
            order = self.get_orders().filter(id=order_id).first()
            if not order:
                return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = RiderOrderSerializer(order)
            return Response(serializer.data)

        orders = self.get_orders().order_by("-created_at")
        serializer = RiderOrderSerializer(orders, many=True)
        return Response({"orders": serializer.data})

    def post(self, request, order_id, action, **kwargs):
        rider = getattr(request.user, "rider_profile", None)
        if not rider:
            return Response({"error": "Rider profile not found."}, status=status.HTTP_404_NOT_FOUND)

        order = OrdersOrder.objects.filter(id=order_id, order_type="delivery").first()
        if not order:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        customer_name = get_customer_name(order)

        if action == "picked_up":
            if order.status != "ready_for_pickup":
                return Response(
                    {"error": f"Order #{order.id} for {customer_name} is not ready for pickup yet."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.status = "picked_up"
            order.save()
            return Response(
                order_response(f"Order #{order.id} for {customer_name} has been picked up. Head to the delivery address!", order),
                status=status.HTTP_200_OK
            )

        elif action == "out_for_delivery":
            if order.status != "picked_up":
                return Response(
                    {"error": f"Order #{order.id} for {customer_name} must be picked up before marking as out for delivery."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.status = "out_for_delivery"
            order.save()
            return Response(
                order_response(f"Order #{order.id} for {customer_name} is now out for delivery.", order),
                status=status.HTTP_200_OK
            )

        elif action == "complete":
            if order.status != "out_for_delivery":
                return Response(
                    {"error": f"Order #{order.id} for {customer_name} must be out for delivery before completing."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.status = "completed"
            order.save()
            return Response(
                order_response(f"Order #{order.id} for {customer_name} has been delivered successfully!", order),
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"error": f"Invalid action '{action}'."},
                status=status.HTTP_400_BAD_REQUEST
            )