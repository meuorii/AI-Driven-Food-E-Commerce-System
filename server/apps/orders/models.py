from django.db import models

# Create your models here.
class OrdersOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('picked_up', 'Picked Up by Rider'),
        ('out_for_delivery', 'Out for Delivery'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('gcash', 'GCash'),
        ('card', 'Card'),
    ]

    ORDER_TYPE_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    ]

    id = models.BigAutoField(primary_key=True)
    order_code = models.CharField(max_length=20, unique=True, null=True, blank=True )
    customer = models.ForeignKey('users.UsersCustomerprofile', on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    stall = models.ForeignKey('vendors.VendorsStall', on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    delivery_address = models.TextField(blank=True, null=True)
    cancelled_by = models.CharField(max_length=20, choices=[("customer", "Customer"), ("vendor", "Vendor")], null=True, blank=True )
    cancel_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders_order'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_code}"


class OrdersOrderitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(OrdersOrder, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey('products.ProductsFooditem', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'orders_orderitem'
        unique_together = ('order', 'food_item')

    def __str__(self):
        return f"{self.order.order_code} - {self.food_item.name}"
