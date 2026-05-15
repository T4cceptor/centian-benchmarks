import unittest

from user_payload import build_user_create_payload


class FreePlanRoleRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        """Free-plan tenants must not have a 'role' key in the user dict."""
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn(
            "role",
            result["user"],
            "role must be omitted entirely for free-plan tenants",
        )

    def test_free_plan_tenant_omits_role_even_when_caller_provides_one(self):
        """Even if the caller passes a role, it must be discarded for free-plan tenants."""
        user = {"email": "bob@example.com", "display_name": "Bob", "role": "admin"}
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn(
            "role",
            result["user"],
            "caller-provided role must be discarded for free-plan tenants",
        )


if __name__ == "__main__":
    unittest.main()
