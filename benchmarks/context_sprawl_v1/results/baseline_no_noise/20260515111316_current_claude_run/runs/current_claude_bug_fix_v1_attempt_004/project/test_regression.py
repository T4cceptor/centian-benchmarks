import unittest

from user_payload import build_user_create_payload


class FreeplanRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        """Free-plan tenants must not have a role field in the payload."""
        user = {"email": "user@example.com", "display_name": "Test User"}
        result = build_user_create_payload(user, "free_tenant_123")
        self.assertNotIn("role", result["user"])

    def test_free_plan_tenant_with_provided_role_omits_role(self):
        """Even if caller provides a role, free-plan must omit it."""
        user = {
            "email": "user@example.com",
            "display_name": "Test User",
            "role": "admin",
        }
        result = build_user_create_payload(user, "free_tenant_456")
        self.assertNotIn("role", result["user"])

    def test_non_free_plan_tenant_includes_role(self):
        """Non-free tenants should include role field (defaults to 'member')."""
        user = {"email": "user@example.com", "display_name": "Test User"}
        result = build_user_create_payload(user, "standard_tenant_123")
        self.assertIn("role", result["user"])
        self.assertEqual(result["user"]["role"], "member")


if __name__ == "__main__":
    unittest.main()
