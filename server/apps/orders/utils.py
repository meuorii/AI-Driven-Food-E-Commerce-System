from apps.vendors.models import VendorActivityLog
from apps.users.models import RiderActivityLog

PRONOUNS = {
    "MALE": "He",
    "FEMALE": "She",
    "OTHER": "They",
    "PREFER_NOT": "They",
}


def log_order_activity(vendor, action_type, order, stall=None):
    gender = vendor.gender or "PREFER_NOT"
    pronoun = PRONOUNS.get(gender, "They")

    if action_type == "Confirmed order":
        action_message = f"{pronoun} confirmed order {order.order_code}."

    elif action_type == "Cancelled order":
        action_message = f"{pronoun} cancelled order {order.order_code} with reason: '{order.cancel_reason}'."

    elif action_type == "Preparing order":
        action_message = f"{pronoun} started preparing order {order.order_code}."

    elif action_type == "Ready order":
        if order.order_type == "delivery":
            action_message = f"{pronoun} marked order {order.order_code} as ready and assigned a rider."
        else:
            action_message = f"{pronoun} marked order {order.order_code} as ready for pickup."

    elif action_type == "Completed order":
        action_message = f"{pronoun} completed order {order.order_code}."

    else:
        action_message = f"{pronoun} performed an action: {action_type}."

    VendorActivityLog.objects.create(
        vendor=vendor,
        action=action_message,
        stall=stall,
        order=order,
    )


def log_rider_activity(rider, action_type, order=None):
    gender = rider.gender or "PREFER_NOT"
    pronoun = PRONOUNS.get(gender, "They")

    customer_name = None
    if order:
        profile = order.customer
        first = profile.first_name or ""
        last = profile.last_name or ""
        customer_name = f"{first} {last}".strip() or profile.user.email

    if action_type == "picked_up":
        action_message = f"{pronoun} picked up order {order.order_code} for {customer_name}."

    elif action_type == "out_for_delivery":
        action_message = f"{pronoun} is now out for delivery for order {order.order_code} to {customer_name}."

    elif action_type == "completed":
        action_message = f"{pronoun} successfully delivered order {order.order_code} to {customer_name}."

    else:
        action_message = f"{pronoun} performed an action: {action_type}."

    RiderActivityLog.objects.create(
        rider=rider,
        action=action_message,
        order=order,
    )