import unittest

from user_payload import build_user_create_payload


class TestFreePlanRoleOmission(unittest.TestCase):
    """Regression: free-plan tenants must not have 'role' in the payload."""

    def test_free_plan_tenant_payload_omits_role(self):
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn(
            "role",
            result["user"],
            "Free-plan tenant payload must not contain 'role' key",
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
            "Free-plan tenant payload must discard caller-provided role",
        )


if __name__ == "__main__":
    unittest.main()
