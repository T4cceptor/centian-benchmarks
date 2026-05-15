import unittest

from user_payload import build_user_create_payload


class FreePlanRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role_from_payload(self):
        """Free-plan tenants must not have 'role' in the user payload."""
        user = {"email": "alice@example.com", "display_name": "Alice", "role": "admin"}
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn(
            "role",
            result["user"],
            "role must be omitted entirely for free-plan tenants",
        )

    def test_free_plan_tenant_omits_role_even_when_not_provided(self):
        """Free-plan tenants must not have 'role' even when caller omits it."""
        user = {"email": "bob@example.com", "display_name": "Bob"}
        result = build_user_create_payload(user, "free_basic")
        self.assertNotIn(
            "role",
            result["user"],
            "role must be omitted entirely for free-plan tenants even with no caller role",
        )


if __name__ == "__main__":
    unittest.main()
