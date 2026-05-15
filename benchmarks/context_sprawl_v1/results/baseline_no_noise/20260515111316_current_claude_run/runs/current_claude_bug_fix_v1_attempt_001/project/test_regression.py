import unittest

from user_payload import build_user_create_payload


class FreeplanRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role_field(self):
        """Free-plan tenants must not have a role field in the payload."""
        user = {"email": "user@example.com", "display_name": "Test User"}
        result = build_user_create_payload(user, "free_plan_tenant")
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
