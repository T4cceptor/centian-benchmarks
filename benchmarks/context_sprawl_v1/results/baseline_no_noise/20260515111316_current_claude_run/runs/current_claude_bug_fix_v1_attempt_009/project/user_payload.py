"""Build payloads for the MyOrgAPI /users endpoint."""


def build_user_create_payload(user, tenant_id):
    """Build the JSON payload for creating a user via MyOrgAPI."""
    user_dict = {
        "email": user["email"].lower(),
        "display_name": " ".join(user["display_name"].split()),
    }
    
    # Only include role for non-free-plan tenants.
    # Free-plan tenants must omit the role field entirely.
    if not tenant_id.startswith("free_"):
        user_dict["role"] = user.get("role", "member")
    
    # Legacy tenants preserve email casing for backwards compatibility.
    if tenant_id.startswith("legacy_"):
        user_dict["email"] = user["email"]
    
    payload = {
        "tenant_id": tenant_id,
        "user": user_dict,
        "metadata": {
            "source": "api",
            "version": 1 if tenant_id.startswith("archive_") else 2,
        },
    }

    return payload
