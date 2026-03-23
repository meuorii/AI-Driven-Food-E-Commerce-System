from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from rest_framework.exceptions import PermissionDenied
from django.db import connection
from django.shortcuts import get_object_or_404
from .models import ProductsCategory, ProductsFooditem, CartItem
from apps.vendors.models import VendorsStall
from .serializers import ProductsCategorySerializer, ProductsFooditemSerializer, StallSerializer, FoodItemSerializer, CartItemSerializer
from .utils import log_product_activity
from .permissions import IsCustomer
from decimal import Decimal
from apps.notifications.utils import (
    notify_category_created,   
    notify_category_updated,   
    notify_category_deleted,
    notify_food_item_created,
    notify_food_item_toggled,
    notify_food_item_updated
)

# Vendor Category View
class VendorCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def _check_stall(self, request, stall_id):
        try:
            stall = VendorsStall.objects.get(id=stall_id, vendor=request.user.vendor_profile)
        except VendorsStall.DoesNotExist:
            raise PermissionDenied("You cannot access another stall.")
        return stall

    def get(self, request, stall_id, category_id=None):
        stall = self._check_stall(request, stall_id)

        if category_id:
            category = get_object_or_404(ProductsCategory, id=category_id, stall=stall)
            serializer = ProductsCategorySerializer(category)
            return Response(serializer.data)

        categories = ProductsCategory.objects.filter(stall=stall)
        serializer = ProductsCategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request, stall_id):
        stall = self._check_stall(request, stall_id)
        serializer = ProductsCategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save(stall=stall)
            log_product_activity(
                vendor=request.user.vendor_profile,
                action_type="Created category",
                stall=stall,
                category=category
            )
            notify_category_created(category, request.user.vendor_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, stall_id, category_id):
        stall = self._check_stall(request, stall_id)
        category = get_object_or_404(ProductsCategory, id=category_id, stall=stall) 
        old_name = category.name
        old_data = ProductsCategorySerializer(category).data
        serializer = ProductsCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            category = serializer.save()
            log_product_activity(
                vendor=request.user.vendor_profile,
                action_type="Updated category",
                stall=stall,
                category=category,
                old_data=old_data,
                new_data=serializer.data
            )
            notify_category_updated(category, request.user.vendor_profile, old_name)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, stall_id, category_id):
        stall = self._check_stall(request, stall_id)
        category = get_object_or_404(ProductsCategory, id=category_id, stall=stall)
        deleted_name = category.name
        category.delete()
        log_product_activity(
            vendor=request.user.vendor_profile,
            action_type="Deleted category",
            stall=stall,
            deleted_name=deleted_name
        )
        notify_category_deleted(stall.name, deleted_name, request.user.vendor_profile)
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
# Vendor Food Item View
class VendorFoodItemView(APIView):
    permission_classes = [IsAuthenticated]

    def _check_stall(self, request, stall_id):
        try:
            return VendorsStall.objects.get(id=stall_id, vendor=request.user.vendor_profile)
        except:
            raise PermissionDenied("You cannot access another stall.")
    
    def get(self, request, stall_id, category_id=None, fooditem_id=None):
        stall = self._check_stall(request, stall_id)
        queryset = ProductsFooditem.objects.filter(stall=stall)
        if category_id:
            get_object_or_404(ProductsCategory, id=category_id, stall=stall)
            queryset = queryset.filter(category_id=category_id)

        if fooditem_id:
            food_item = get_object_or_404(queryset, id=fooditem_id)
            serializer = ProductsFooditemSerializer(food_item)
            return Response(serializer.data)
        
        serializer = ProductsFooditemSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request, stall_id, *args, **kwargs):
        stall = self._check_stall(request, stall_id)
        category_id = kwargs.get('category_id')
        category = get_object_or_404(ProductsCategory, id=category_id, stall=stall)
        serializer = ProductsFooditemSerializer(data=request.data)
        if serializer.is_valid():
            food_item = serializer.save(
                stall=stall,
                category=category,
                is_available=True,
                is_active=True
            )
            log_product_activity(
                vendor=request.user.vendor_profile,
                action_type="Created food item",
                stall=stall,
                food_item=food_item
            )
            notify_food_item_created(food_item, request.user.vendor_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, stall_id, fooditem_id):
        stall = self._check_stall(request, stall_id)
        food_item = get_object_or_404(ProductsFooditem, id=fooditem_id, stall=stall)
        old_data = ProductsFooditemSerializer(food_item).data
        serializer = ProductsFooditemSerializer(food_item, data=request.data, partial=True)
        if serializer.is_valid():
            food_item = serializer.save()
            new_data = ProductsFooditemSerializer(food_item).data
            changes = {k: {"old": old_data[k], "new": new_data[k]} for k in old_data if old_data[k] != new_data[k]}
            log_product_activity(
                vendor=request.user.vendor_profile,
                action_type="Updated food item",
                stall=stall,
                food_item=food_item,
                old_data=old_data,
                new_data=serializer.data
            )
            notify_food_item_updated(food_item, request.user.vendor_profile, changes) 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, stall_id, fooditem_id):
        stall = self._check_stall(request, stall_id)
        food_item = get_object_or_404(ProductsFooditem, id=fooditem_id, stall=stall)
        deleted_name = food_item.name
        food_item.delete()
        log_product_activity(
            vendor=request.user.vendor_profile,
            action_type="Deleted food item",
            stall=stall,
            deleted_name=deleted_name
        )
        return Response({ "message": "Food Item Delete Successfully" }, status=status.HTTP_204_NO_CONTENT)

class VendorFoodItemToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def _check_stall(self, request, stall_id):
        try:
            return VendorsStall.objects.get(id=stall_id, vendor=request.user.vendor_profile)
        except VendorsStall.DoesNotExist:
            raise PermissionDenied("You cannot access another stall.")
        
    def post(self, request, stall_id, fooditem_id):
        stall = self._check_stall(request, stall_id)
        food_item = get_object_or_404(ProductsFooditem, id=fooditem_id, stall=stall)
        food_item.is_active = not food_item.is_active
        food_item.is_available = not food_item.is_available
        food_item.save(update_fields=['is_active', 'is_available'])
        log_product_activity(
            vendor=request.user.vendor_profile,
            action_type="Toggled food item",
            stall=stall,
            food_item=food_item
        )
        notify_food_item_toggled(food_item, request.user.vendor_profile)
        return Response({
            "message": "Food item status toggled successfully",
            "is_active": food_item.is_active,
            "is_available": food_item.is_available
        }, status=status.HTTP_200_OK)

# Get All Products
class AllFoodItemsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        food_items = ProductsFooditem.objects.all()
        serializer = ProductsFooditemSerializer(food_items, many=True)
        return Response(serializer.data)
    
class FoodItemsByStallView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, stall_id):
        stall = get_object_or_404(VendorsStall, id=stall_id)
        food_items = ProductsFooditem.objects.filter(stall=stall)
        serializer = ProductsFooditemSerializer(food_items, many=True)
        return Response(serializer.data)
    
class FoodItemsByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, category_id):
        category = get_object_or_404(ProductsCategory, id=category_id)
        food_items = ProductsFooditem.objects.filter(category=category)
        serializer = ProductsFooditemSerializer(food_items, many=True)
        return Response(serializer.data)
    
class FoodItemsByStallAndCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, stall_id, category_id):
        stall = get_object_or_404(VendorsStall, id=stall_id)
        category = get_object_or_404(ProductsCategory, id=category_id)
        food_items = ProductsFooditem.objects.filter(stall=stall, category=category)
        serializer = ProductsFooditemSerializer(food_items, many=True)
        return Response(serializer.data)
    
#Customer
class CustomerStallListView(generics.ListAPIView):
    queryset = VendorsStall.objects.filter(is_approved=True, is_open=True)
    serializer_class = StallSerializer
    permission_classes = [IsCustomer]

class CustomerFoodItemListView(generics.ListAPIView):
    queryset = ProductsFooditem.objects.filter(
        is_available=True,
        is_active=True,
        stall__is_approved=True, 
        stall__is_open=True
    )
    serializer_class = FoodItemSerializer
    permission_classes = [IsCustomer]

# Get single food item details
class CustomerFoodItemDetailView(generics.RetrieveAPIView):
    queryset = ProductsFooditem.objects.filter(
        is_available=True,
        is_active=True,
        stall__is_approved=True,
        stall__is_open=True
    )
    serializer_class = FoodItemSerializer
    permission_classes = [IsCustomer]
    lookup_field = 'id'

class CartView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        customer = request.user.customer_profile
        cart_items = CartItem.objects.filter(customer=customer)
        serializer = CartItemSerializer(cart_items, many=True)
        total_cart_price = sum([item.total_price for item in cart_items], Decimal('0.00'))
        total_cart_price = "{:.2f}".format(total_cart_price)
        return Response({
            "cart_items": serializer.data,
            "total_cart_price": total_cart_price
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        customer = request.user.customer_profile
        food_item_id = request.data.get("food_item")
        quantity = int(request.data.get("quantity", 1))
        if not food_item_id:
            return Response({"message": "food_item is required."}, status=status.HTTP_400_BAD_REQUEST)
        food_item = get_object_or_404(ProductsFooditem, id=food_item_id)
        if quantity > food_item.stock_quantity:
            return Response({"message": f"Cannot add {quantity} {food_item.name} to cart. Only {food_item.stock_quantity} available."}, status=status.HTTP_400_BAD_REQUEST)
        cart_item, created = CartItem.objects.get_or_create(
            customer=customer,
            stall=food_item.stall,
            food_item=food_item,
            defaults={"quantity": quantity}
        )
        if not created:
            return Response({"message": f"{food_item.name} is already in your cart."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CartItemSerializer(cart_item)
        return Response({"message": f"{food_item.name} added to cart successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
    
    def patch(self, request, cart_id):
        customer = request.user.customer_profile 
        cart_item = get_object_or_404(CartItem, id=cart_id, customer=customer)
        quantity = request.data.get("quantity")
        if quantity is None or int(quantity) < 1:
            return Response({"message": "Quantity must be a positive integer."}, status=status.HTTP_400_BAD_REQUEST)
        quantity = int(quantity)
        if quantity > cart_item.food_item.stock_quantity:
            return Response({"message": f"Cannot set quantity to {quantity}. Only {cart_item.food_item.stock_quantity} {cart_item.food_item.name} available."}, status=status.HTTP_400_BAD_REQUEST)
        cart_item.quantity = int(quantity)
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response({"message": f"{cart_item.food_item.name} quantity updated to {cart_item.quantity}.", "data": serializer.data}, status=status.HTTP_200_OK)
    
    def delete(Self, request, cart_id):
        customer = request.user.customer_profile
        cart_item = get_object_or_404(CartItem, id=cart_id, customer=customer)
        food_name = cart_item.food_item.name
        cart_item.delete()
        return Response({"message": f"{food_name} removed from cart."}, status=status.HTTP_204_NO_CONTENT)
            