from django.db import models
from django.utils import timezone

# Create your models here.
class VendorsStall(models.Model):
    id = models.BigAutoField(primary_key=True)
    vendor = models.ForeignKey('users.UsersVendorprofile', models.DO_NOTHING)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='vendors/logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='vendors/banners/', blank=True, null=True)
    is_open = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'vendors_stall'