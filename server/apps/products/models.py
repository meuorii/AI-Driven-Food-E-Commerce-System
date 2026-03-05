from django.db import models

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