"""Build payloads for the MyOrgAPI /users endpoint."""


def build_user_create_payload(user, tenant_id):
    """Build the JSON payload for creating a user via MyOrgAPI."""
    payload = {
        "tenant_id": tenant_id,
        "user": {
            "email": user["email"].lower(),
            "display_name": " ".join(user["display_name"].split()),
        },
        "metadata": {
            "source": "api",
            "version": 1 if tenant_id.startswith("archive_") else 2,
        },
    }

    # Legacy tenants preserve email casing for backwards compatibility.
    if tenant_id.startswith("legacy_"):
        payload["user"]["email"] = user["email"]

    # Free-plan tenants must omit the role field.
    if not tenant_id.startswith("free_"):
        payload["user"]["role"] = user.get("role", "member")

    return payload
