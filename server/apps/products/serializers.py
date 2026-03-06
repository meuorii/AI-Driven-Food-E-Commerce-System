from rest_framework import serializers
from apps.vendors.models import VendorsStall
from .models import ProductsCategory, ProductsFooditem

class ProductsCategorySerializer(serializers.ModelSerializer):
    stall = serializers.PrimaryKeyRelatedField(read_only=True) 
    is_active = serializers.BooleanField(default=True) 

    class Meta:
        model = ProductsCategory
        fields = ['id', 'stall', 'name', 'slug', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['stall', 'created_at', 'updated_at']

class ProductsFooditemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsFooditem
        fields = ['id', 'category', 'name', 'description', 'image', 'price', 'stock_quantity', 'is_available', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'is_available', 'is_active', 'category']

class StallSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorsStall
        fields = ['id', 'name', 'description', 'logo', 'banner', 'is_open', 'is_approved']

class FoodItemSerializer(serializers.ModelSerializer):
    stall = StallSerializer(read_only=True)
    category = serializers.StringRelatedField() 

    class Meta:
        model = ProductsFooditem
        fields = ['id', 'stall', 'category', 'name', 'description', 'price', 'stock_quantity', 'is_available']