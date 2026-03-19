from django.db import models
from django.utils import timezone

# Create your models here.
class VendorsStall(models.Model):
    id = models.BigAutoField(primary_key=True)
    vendor = models.ForeignKey('users.UsersVendorprofile', models.DO_NOTHING, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='vendors/logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='vendors/banners/', blank=True, null=True)
    is_open = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'vendors_stall'

class VendorActivityLog(models.Model):
    vendor = models.ForeignKey('users.UsersVendorprofile', on_delete=models.CASCADE, related_name='activities') 
    action = models.CharField(max_length=255)
    stall = models.ForeignKey('vendors.VendorsStall', on_delete=models.SET_NULL, null=True, blank=True)
    food_item = models.ForeignKey('products.ProductsFooditem', on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey('products.ProductsCategory', on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey('orders.OrdersOrder', on_delete=models.SET_NULL, null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.vendor.id} - {self.action}"