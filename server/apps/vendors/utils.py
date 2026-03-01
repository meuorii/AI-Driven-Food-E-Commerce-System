from .models import VendorActivityLog

PRONOUNS = {
    "MALE": "He",
    "FEMALE": "She",
    "OTHER": "They",
    "PREFER_NOT": "They",
}

def log_vendor_activity(vendor, action_type, stall=None):
    gender = vendor.gender or "PREFER_NOT"
    pronoun = PRONOUNS.get(gender, "They")

    if action_type == "Created stall":
        action_message = f"{pronoun} created a new stall named '{stall.name}'."
    elif action_type == "Updated stall":
        action_message = f"{pronoun} updated the stall named '{stall.name}'."
    elif action_type == "Toggled stall":
        if stall:
            status = "open" if stall.is_open else "closed"
            action_message = f"{pronoun} {status} the stall '{stall.name}'."
        else:
            action_message = f"{pronoun} toggled the stall status."
    else:
        action_message = f"{pronoun} performed an action: {action_type}."
    VendorActivityLog.objects.create(vendor=vendor, action=action_message, stall=stall)