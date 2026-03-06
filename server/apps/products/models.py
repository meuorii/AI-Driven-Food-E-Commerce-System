from django.db import models
from apps.users.models import UsersCustomerprofile
from apps.vendors.models import VendorsStall

# Create your models here.
class ProductsCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    stall = models.ForeignKey('vendors.VendorsStall', on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(unique=True, max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'products_category'


class ProductsFooditem(models.Model):
    id = models.BigAutoField(primary_key=True)
    stall = models.ForeignKey('vendors.VendorsStall', on_delete=models.CASCADE, related_name='food_items')
    category = models.ForeignKey(ProductsCategory, on_delete=models.CASCADE, related_name='food_items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    promo_start = models.DateTimeField(null=True, blank=True)
    promo_end = models.DateTimeField(null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'products_fooditem'

    def save(self, *args, **kwargs):
        if self.stock_quantity == 0:
            self.is_active = False
            self.is_available = False
        super().save(*args, **kwargs)

class CartItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(UsersCustomerprofile, on_delete=models.CASCADE, related_name='cart_items')
    stall = models.ForeignKey(VendorsStall, on_delete=models.CASCADE, related_name='cart_items')
    food_item = models.ForeignKey(ProductsFooditem, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products_cartitem'
        unique_together = ('customer', 'stall', 'food_item') 
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.customer.user.email} - {self.food_item.name} ({self.quantity})"
    
    @property
    def total_price(self):
        return self.quantity * self.food_item.price