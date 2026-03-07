from rest_framework import serializers
from apps.vendors.models import VendorsStall
from .models import ProductsCategory, ProductsFooditem, CartItem

class ProductsCategorySerializer(serializers.ModelSerializer):
    stall = serializers.PrimaryKeyRelatedField(read_only=True) 
    is_active = serializers.BooleanField(default=True) 

    class Meta:
        model = ProductsCategory
        fields = ['id', 'stall', 'name', 'slug', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['stall', 'created_at', 'updated_at']

class ProductsFooditemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
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
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = ProductsFooditem
        fields = ['id', 'stall', 'category', 'name', 'description', 'image', 'price', 'stock_quantity', 'is_available']

class CartItemSerializer(serializers.ModelSerializer):
    food_item_name = serializers.CharField(source="food_item.name", read_only=True)
    food_item_price = serializers.DecimalField(source="food_item.price", max_digits=10, decimal_places=2, read_only=True)
    food_item_image = serializers.ImageField(source="food_item.image", read_only=True)
    stall_name = serializers.CharField(source="stall.name", read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "stall",
            "stall_name",
            "food_item",
            "food_item_name",
            "food_item_price",
            "food_item_image",
            "quantity",
            "total_price",
            "added_at",
            "updated_at"
        ]
        read_only = ["added_at", "updated_at"]