from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.db import connection
from django.shortcuts import get_object_or_404
from .models import ProductsCategory, ProductsFooditem
from apps.vendors.models import VendorsStall
from .serializers import ProductsCategorySerializer, ProductsFooditemSerializer
from .utils import log_product_activity

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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, stall_id, category_id):
        stall = self._check_stall(request, stall_id)
        category = get_object_or_404(ProductsCategory, id=category_id, stall=stall) 
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, stall_id, fooditem_id):
        stall = self._check_stall(request, stall_id)
        food_item = get_object_or_404(ProductsFooditem, id=fooditem_id, stall=stall)
        old_data = ProductsFooditemSerializer(food_item).data
        serializer = ProductsFooditemSerializer(food_item, data=request.data, partial=True)
        if serializer.is_valid():
            food_item = serializer.save()
            log_product_activity(
                vendor=request.user.vendor_profile,
                action_type="Updated food item",
                stall=stall,
                food_item=food_item,
                old_data=old_data,
                new_data=serializer.data
            )

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