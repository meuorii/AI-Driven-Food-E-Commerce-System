from apps.users.models import UsersUser
from .models import NotificationsNotification

def notify(user, title, message, notification_type=None, order=None):
    NotificationsNotification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        order=order,
    )

def get_admin_users():
    return UsersUser.objects.filter(role='ADMIN', is_active=True)

def notify_admins(title, message, notification_type=None, order=None):
    for admin in get_admin_users():
        notify(admin, title, message, notification_type, order)

def get_customer_name(order):
    profile = order.customer
    first = profile.first_name or ""
    last = profile.last_name or ""
    return f"{first} {last}".strip() or profile.user.email

# Order Placed
def notify_order_placed(order):
    customer_user = order.customer.user
    customer_name = get_customer_name(order)
    stall_name = order.stall.name
    vendor_user = order.stall.vendor.user
    notify(customer_user, title="Order Placed Successfully!", message=f"Your order {order.order_code} from {stall_name} has been placed and is awaiting confirmation.", notification_type="order_placed", order=order)
    notify(vendor_user, title="New Order Received!", message=f"You have a new order {order.order_code} from {customer_name}. Please confirm it.", notification_type="order_placed", order=order)
    notify_admins(title="New Order Placed", message=f"Customer {customer_name} placed order {order.order_code} from stall'{stall_name}'.", notification_type="order_placed", order=order)

# Order Confirmed
def notify_order_confirmed(order):
    customer_name = get_customer_name(order)
    stall_name = order.stall.name
    notify(order.customer.user, title="Order Confirmed!", message=f"Your Order {order.order_code} from {stall_name} has been confirmed and will be prepared soon.", notification_type="order_confirmed", order=order)
    notify_admins(title="Order Confirmed", message=f"Order {order.order_code} for {customer_name} has been confirmed by the Vendor '{stall_name}'.", notification_type="order_confirmed", order=order)

# Order Prepared
def notify_order_preparing(order):
    customer_name = get_customer_name(order)
    stall_name = order.stall.name
    notify(order.customer.user, title="Order Being Prepared!", message=f"Your Order {order.order_code} from {stall_name} is now being prepared. Hang tight!", notification_type="order_preparing", order=order)
    notify_admins(title="Order Being Prepared", message=f"Order {order.order_code} for {customer_name} is now being prepared by vendor '{stall_name}'.", notification_type="order_preparing", order=order)

# Order Ready
def notify_order_ready(order):
    customer_name = get_customer_name(order)
    stall_name = order.stall.name
    rider_name = f"{order.rider.first_name} {order.rider.last_name}".strip() if order.rider else "a rider"
    if order.order_type == "pickup":
        notify(order.customer.user, title="Order Ready for Pickup!", message=f"Your order {order.order_code} from {stall_name} is ready! Please come and pick it up", notification_type="order_ready", order=order)
        notify_admins(title="Order Ready for Pickup", message=f"Order {order.order_code} for {customer_name} is ready for pickup at '{stall_name}'.", notification_type="order_ready", order=order)
    else:
        notify(order.customer.user, title="Order Ready for Delivery!", message=f"Your Order {order.order_code} is ready and has been assigned to rider {rider_name}. It will be delivered soon!", notification_type="order_ready", order=order)
        if order.rider:
            notify(order.rider.user, title="New Delivery Assigned!", message=f"You have been assigned to deliver order {order.order_code} for {customer_name}. Please pick it up from '{stall_name}'.", notification_type="order_ready", order=order)
        notify_admins(title="Order Ready for Delivery", message=f"Order {order.order_code} for {customer_name} is ready and assigned to rider {rider_name}.", notification_type="order_ready", order=order)

def notify_order_picked_up(order):
    customer_name = get_customer_name(order)
    vendor_user = order.stall.vendor.user
    rider_name = f"{order.rider.first_name} {order.rider.last_name}".strip() if order.rider else "The rider"
    notify(order.customer.user, title="Order Picked Up!", message=f"Your order {order.order_code} has been picked up by {rider_name} and will be on its way soon!.", notification_type="order_picked_up", order=order)
    notify(vendor_user, title="Order Picked Up by Rider", message=f"Order {order.order_code} for {customer_name} has been picked up by rider {rider_name}.", notification_type="order_picked_up", order=order )
    notify_admins(title="Order Picked up", message=f"Order {order.order_code} for {customer_name} has been picked up by rider {rider_name}.", notification_type="order_picked_up", order=order)

def notify_order_out_for_delivery(order):
    customer_name = get_customer_name(order)
    rider_name = f"{order.rider.first_name} {order.rider.last_name}".strip() if order.rider else "The rider"
    vendor_user = order.stall.vendor.user
    notify(order.customer.user, title="Order Out for Delivery!", message=f"Your order {order.order_code} is on its way! {rider_name} is heading to your location.", notification_type="order_out_for_delivery", order=order)
    notify(vendor_user, title="Order Out for Delivery", message=f"Order {order.order_code} for {customer_name} is now out for delivery by rider {rider_name}.", notification_type="order_out_for_delivery", order=order)
    notify_admins(title="Order Out for Delivery", message=f"Order {order.order_code} for {customer_name} is out for delivery by rider {rider_name}.", notification_type="order_out_for_delivery")

def notify_order_completed(order):
    customer_name = get_customer_name(order)
    stall_name = order.stall.name
    vendor_user = order.stall.vendor.user
    notify(order.customer.user, title="Order Completed!", message=f"Your order {order.order_code} from {stall_name} has been completed. Enjoy your meal!", notification_type="order_completed", order=order)
    notify(vendor_user, title="Order Completed", message=f"Order {order.order_code} for {customer_name} has been successfully completed.", notification_type="order_completed", order=order)
    if order.order_type == "delivery" and order.rider:
        notify(order.rider.user, title="Delivery Completed", message=f"You have successfully delivered order {order.order_code} to {customer_name}. Great job!", notification_type="order_completed", order=order) 
    notify_admins(title="Order Completed", message=f"Order {order.order_code} for {customer_name} from '{stall_name}' has been completed.", notification_type="order_completed", order=order)

def notify_order_cancelled(order):
    customer_name = get_customer_name(order)
    stall_name = order.stall.name
    vendor_user = order.stall.vendor.user
    cancelled_by = order.cancelled_by
    reason = order.cancel_reason or "No reason provided."
    if cancelled_by == "vendor":
        customer_message = f"Your order {order.order_code} from {stall_name} has been cancelled by the vendor. Reason: {reason}"
        vendor_message = f"You have cancelled order {order.order_code} for {customer_name}. Reason: {reason}"
        admin_message = f"Order {order.order_code} for {customer_name} was cancelled by vendor '{stall_name}'. Reason: {reason}"
    else:
        customer_message = f"Your order {order.order_code} from {stall_name} has been cancelled."
        vendor_message = f"Order {order.order_code} from {customer_name} has been cancelled by the customer."
        admin_message = f"Order {order.order_code} for {customer_name} was cancelled by the customer."
    notify(order.customer.user, title="Order Cancelled", message=customer_message, notification_type="order_cancelled", order=order)
    notify(vendor_user, title="Order Cancelled", message=vendor_message, notification_type="order_cancelled", order=order)
    notify_admins(title="Order Cancelled", message=admin_message, notification_type="order_cancelled", order=order)