from .models import VendorActivityLog

PRONOUNS = {
    "MALE": "He",
    "FEMALE": "She",
    "OTHER": "They",
    "PREFER_NOT": "They",
}


def detect_changes(old_data, new_data):
    changes = {}

    for field in old_data:
        if old_data[field] != new_data[field]:
            changes[field] = {
                "old": old_data[field],
                "new": new_data[field]
            }

    return changes


def log_vendor_activity(vendor, action_type, stall=None, old_data=None, new_data=None):
    gender = vendor.gender or "PREFER_NOT"
    pronoun = PRONOUNS.get(gender, "They")

    changes = None

    if action_type == "Updated stall":
        changes = detect_changes(old_data, new_data)

        action_message = f"{pronoun} updated the stall '{stall.name}'."

    elif action_type == "Created stall":
        action_message = f"{pronoun} created a new stall named '{stall.name}'."

    elif action_type == "Toggled stall":
        status = "opened" if stall.is_open else "closed"
        action_message = f"{pronoun} {status} the stall '{stall.name}'."

    elif action_type == "Approved stall":
        action_message = f"Stall '{stall.name}' was approved by an administrator."

    elif action_type == "Rejected stall":
        action_message = f"Stall '{stall.name}' was rejected by an administrator."

    else:
        action_message = f"{pronoun} performed an action: {action_type}."

    VendorActivityLog.objects.create(vendor=vendor, action=action_message, stall=stall, changes=changes)