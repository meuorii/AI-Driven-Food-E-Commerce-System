from django.db import models

# Create your models here.
class OrdersOrder(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey('users.UsersCustomerprofile', models.DO_NOTHING)
    stall = models.ForeignKey('vendors.VendorsStall', models.DO_NOTHING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    payment_method = models.TextField()  # This field type is a guess.
    order_type = models.TextField()  # This field type is a guess.
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders_order'


class OrdersOrderitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(OrdersOrder, models.DO_NOTHING)
    food_item = models.ForeignKey('products.ProductsFooditem', models.DO_NOTHING)
    quantity = models.IntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'orders_orderitem'
