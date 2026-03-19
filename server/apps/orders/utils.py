from apps.vendors.models import VendorActivityLog

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
        action_message = f"{pronoun} confirmed order #{order.id}."

    elif action_type == "Cancelled order":
        action_message = f"{pronoun} cancelled order #{order.id} with reason: '{order.cancel_reason}'."

    elif action_type == "Preparing order":
        action_message = f"{pronoun} started preparing order #{order.id}."

    elif action_type == "Ready order":
        if order.order_type == "delivery":
            action_message = f"{pronoun} marked order #{order.id} as ready and assigned a rider."
        else:
            action_message = f"{pronoun} marked order #{order.id} as ready for pickup."

    elif action_type == "Completed order":
        action_message = f"{pronoun} completed order #{order.id}."

    else:
        action_message = f"{pronoun} performed an action: {action_type}."

    VendorActivityLog.objects.create(
        vendor=vendor,
        action=action_message,
        stall=stall,
        order=order,
    )