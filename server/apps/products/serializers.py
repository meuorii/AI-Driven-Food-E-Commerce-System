from rest_framework import serializers
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