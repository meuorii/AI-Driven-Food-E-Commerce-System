from apps.vendors.models import VendorActivityLog

PRONOUNS = {
    "MALE": "He",
    "FEMALE": "She",
    "OTHER": "They",
    "PREFER_NOT": "They",
}


def detect_changes(old_data, new_data):
    changes = {}

    for field, old_value in old_data.items():
        new_value = new_data.get(field)

        if old_value != new_value:
            changes[field] = {
                "old": old_value,
                "new": new_value
            }

    return changes


def log_product_activity(
    vendor,
    action_type,
    stall=None,
    food_item=None,
    category=None,
    old_data=None,
    new_data=None,
    deleted_name=None
):
    gender = getattr(vendor, "gender", "PREFER_NOT") or "PREFER_NOT"
    pronoun = PRONOUNS.get(gender, "They")

    changes = detect_changes(old_data, new_data) if old_data and new_data else {}

    # FOOD ITEM ACTIONS
    if action_type == "Created food item" and food_item:
        action_message = f"{pronoun} added a new food item '{food_item.name}'."

    elif action_type == "Updated food item" and food_item:
        action_message = f"{pronoun} updated the food item '{food_item.name}'."

    elif action_type == "Toggled food item" and food_item:
        status = "available" if food_item.is_available else "unavailable"
        action_message = f"{pronoun} marked '{food_item.name}' as {status}."

    elif action_type == "Deleted food item":
        action_message = f"{pronoun} deleted the food item '{deleted_name}'."

    # CATEGORY ACTIONS
    elif action_type == "Created category" and category:
        action_message = f"{pronoun} created a new category '{category.name}'."

    elif action_type == "Updated category" and category:
        action_message = f"{pronoun} updated the category '{category.name}'."

    elif action_type == "Deleted category":
        action_message = f"{pronoun} deleted the category '{deleted_name}'."

    else:
        action_message = f"{pronoun} performed action: {action_type}."

    VendorActivityLog.objects.create(
        vendor=vendor,
        action=action_message,
        stall=stall,
        food_item=food_item,
        category=category,
        changes=changes
    )