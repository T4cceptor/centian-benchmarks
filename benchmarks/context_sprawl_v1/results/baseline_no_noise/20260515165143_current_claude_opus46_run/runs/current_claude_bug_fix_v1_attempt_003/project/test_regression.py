import unittest

from user_payload import build_user_create_payload


class TestFreePlanRoleBug(unittest.TestCase):
    """Regression: free-plan tenants must not have 'role' in the payload."""

    def test_free_plan_tenant_omits_role_from_payload(self):
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn(
            "role",
            result["user"],
            "Free-plan tenant payload must not contain the 'role' key",
        )

    def test_free_plan_tenant_discards_explicit_role(self):
        user = {
            "email": "bob@example.com",
            "display_name": "Bob",
            "role": "admin",
        }
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn(
            "role",
            result["user"],
            "Free-plan tenant payload must discard any caller-provided role",
        )


if __name__ == "__main__":
    unittest.main()
