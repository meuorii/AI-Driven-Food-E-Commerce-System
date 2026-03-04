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
        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(MAX(id), 0) FROM products_category;")
            max_id = cursor.fetchone()[0]
            cursor.execute(f"ALTER SEQUENCE products_category_id_seq RESTART WITH {max_id + 1};")
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
            serializer.save(stall=stall, category=category, is_available=True, is_active=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, stall_id, fooditem_id):
        stall = self._check_stall(request, stall_id)
        food_item = get_object_or_404(ProductsFooditem, id=fooditem_id, stall=stall)
        serializer = ProductsFooditemSerializer(food_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, stall_id, fooditem_id):
        stall = self._check_stall(request, stall_id)
        food_item = get_object_or_404(ProductsFooditem, id=fooditem_id, stall=stall)
        food_item.delete()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(MAX(id), 0) FROM products_category;")
            max_id = cursor.fetchone()[0]
            cursor.execute(f"ALTER SEQUENCE products_category_id_seq RESTART WITH {max_id + 1};")
        return Response({ "message": "Food Item Delete Successfully" }, status=status.HTTP_204_NO_CONTENT)
