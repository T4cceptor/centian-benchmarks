import unittest

from user_payload import build_user_create_payload


# TestFreePlanRoleBug::test_free_plan_tenant_omits_role
class TestFreePlanRoleBug(unittest.TestCase):
    """Regression: free-plan tenants must have 'role' omitted entirely."""

    def test_free_plan_tenant_omits_role(self):
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn(
            "role",
            result["user"],
            "Free-plan tenants must not have a 'role' key in the user payload",
        )

    def test_free_plan_tenant_omits_role_even_when_caller_provides_one(self):
        user = {
            "email": "bob@example.com",
            "display_name": "Bob",
            "role": "admin",
        }
        result = build_user_create_payload(user, "free_trial_5")
        self.assertNotIn(
            "role",
            result["user"],
            "Free-plan tenants must discard any caller-provided role",
        )


if __name__ == "__main__":
    unittest.main()
