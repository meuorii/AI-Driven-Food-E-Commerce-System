from django.db import models

# Create your models here.
class VendorsStall(models.Model):
    id = models.BigAutoField(primary_key=True)
    vendor = models.ForeignKey('users.UsersVendorprofile', models.DO_NOTHING)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_open = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vendors_stall'