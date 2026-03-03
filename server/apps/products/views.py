from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import ProductsCategory, ProductsFooditem
from apps.vendors.models import VendorsStall
from .serializers import ProductsCategorySerializer, ProductsFooditemSerializer

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
            serializer.save(stall=stall)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, stall_id, category_id):
        stall = self._check_stall(request, stall_id)
        category = get_object_or_404(ProductsCategory, id=category_id, stall=stall)
        serializer = ProductsCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, stall_id, category_id):
        stall = self._check_stall(request, stall_id)
        category = get_object_or_404(ProductsCategory, id=category_id, stall=stall)
        category.delete()
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
# Vendor Food Item View
class VendorFoodItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, fooditem_id=None):
        vendor_profile = getattr(request.user, 'vendor_profile', None)
        if not vendor_profile:
            return Response([], status=status.HTTP_200_OK)
        
        if fooditem_id:
            food_item = get_object_or_404(ProductsFooditem, id=fooditem_id, stall=vendor_profile)
            serializer = ProductsFooditemSerializer(food_item)
            return Response(serializer.data)
        
        food_items = ProductsFooditem.objects.filter(stall=vendor_profile)
        serializer = ProductsFooditemSerializer(food_items, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        vendor_profile = getattr(request.user, 'vendor_profile', None)
        if not vendor_profile:
            raise PermissionDenied("You do not have stall.")
        
        serializer = ProductsFooditemSerializer(data=request.data)  
        if serializer.is_valid():
            serializer.save(stall=vendor_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, fooditem_id):
        vendor_profile = getattr(request.user, 'vendor_profile', None)
        food_item = get_object_or_404(ProductsFooditem, id=fooditem_id, stall=vendor_profile)
        serializer = ProductsFooditemSerializer(food_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, fooditem_id):
        vendor_profile = getattr(request.user, 'vendor_profile', None)
        food_item = get_object_or_404(ProductsFooditem, id=fooditem_id, stall=vendor_profile)
        food_item.delete()
        return Response({"message": "Food item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
# Food Item by Category
class VendorFoodItemByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, category_id):
        vendor_profile = getattr(request.user, 'vendor_profile', None)
        if not vendor_profile:
            return Response([], status=status.HTTP_200_OK)
        
        get_object_or_404(ProductsCategory, id=category_id, stall=vendor_profile)
        
        food_items = ProductsFooditem.objects.filter(stall=vendor_profile, category_id=category_id)
        serializer = ProductsFooditemSerializer(food_items, many=True)
        return Response(serializer.data)
