import unittest

from user_payload import build_user_create_payload


class TestFreePlanRoleOmitted(unittest.TestCase):
    """Regression: free-plan tenants must not have 'role' in the payload."""

    def test_free_plan_tenant_omits_role_no_role_provided(self):
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn(
            "role",
            result["user"],
            "role key must be omitted for free-plan tenants",
        )

    def test_free_plan_tenant_omits_role_even_when_caller_provides_role(self):
        user = {
            "email": "bob@example.com",
            "display_name": "Bob",
            "role": "admin",
        }
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn(
            "role",
            result["user"],
            "role key must be omitted for free-plan tenants even if caller supplies one",
        )


if __name__ == "__main__":
    unittest.main()
