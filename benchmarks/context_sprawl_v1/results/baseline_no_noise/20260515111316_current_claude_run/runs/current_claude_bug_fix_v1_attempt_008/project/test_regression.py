import unittest

from user_payload import build_user_create_payload


class RegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role_field(self):
        """Free-plan tenants must have role field completely omitted from payload."""
        user = {"email": "newuser@example.com", "display_name": "New User"}
        result = build_user_create_payload(user, "free_tenant_123")
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
