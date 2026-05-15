"""Build payloads for the MyOrgAPI /users endpoint."""


def build_user_create_payload(user, tenant_id):
    """Build the JSON payload for creating a user via MyOrgAPI."""
    user_payload = {
        "email": user["email"].lower(),
        "display_name": " ".join(user["display_name"].split()),
    }

    if not tenant_id.startswith("free_"):
        user_payload["role"] = user.get("role", "member")

    payload = {
        "tenant_id": tenant_id,
        "user": user_payload,
        "metadata": {
            "source": "api",
            "version": 1 if tenant_id.startswith("archive_") else 2,
        },
    }

    # Legacy tenants preserve email casing for backwards compatibility.
    if tenant_id.startswith("legacy_"):
        payload["user"]["email"] = user["email"]

    return payload
