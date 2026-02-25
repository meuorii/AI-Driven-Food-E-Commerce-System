from django.db import models

# Create your models here.
class ProductsCategory(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'products_category'


class ProductsFooditem(models.Model):
    id = models.UUIDField(primary_key=True)
    stall = models.ForeignKey('vendors.VendorsStall', models.DO_NOTHING)
    category = models.ForeignKey(ProductsCategory, models.DO_NOTHING)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(blank=True, null=True)
    is_available = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products_fooditem'