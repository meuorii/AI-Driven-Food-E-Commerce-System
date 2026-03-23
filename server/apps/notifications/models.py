from django.db import models
from django.utils import timezone
class NotificationsNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('order_placed', 'Order Placed'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_preparing', 'Order Preparing'),
        ('order_ready', 'Order Ready'),
        ('order_picked_up', 'Order Picked Up'),
        ('order_out_for_delivery', 'Order Out for Delivery'),
        ('order_completed', 'Order Completed'),
        ('order_cancelled', 'Order Cancelled'),
        ('account_approved', 'Account Approved'),
        ('account_rejected', 'Account Rejected'),
        ('account_suspended', 'Account Suspended'),
        ('account_unsuspended', 'Account Unsuspended'),
        ('account_pending', 'Account Pending Approval'),
        ('stall_created', 'Stall Created'),
        ('stall_updated', 'Stall Updated'),
        ('stall_toggled', 'Stall Toggled'),
        ('stall_approved', 'Stall Approved'),
        ('stall_rejected', 'Stall Rejected'),
        ('stall_created', 'Stall Created'),
        ('stall_updated', 'Stall Updated'),
        ('stall_toggled', 'Stall Toggled'),
        ('stall_approved', 'Stall Approved'),
        ('stall_rejected', 'Stall Rejected'),
        ('category_created', 'Category Created'),
        ('category_updated', 'Category Updated'),
        ('category_deleted', 'Category Deleted'),
        ('food_item_created', 'Food Item Created'),
        ('food_item_toggled', 'Food Item Toggled'),
        ('food_item_updated', 'Food Item Updated'),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('users.UsersUser', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, null=True, blank=True)
    order = models.ForeignKey('orders.OrdersOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'notifications_notification'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"