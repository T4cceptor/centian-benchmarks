import unittest

from user_payload import build_user_create_payload


class TestFreeplanUserRegression(unittest.TestCase):
    # Regression test for free-plan tenant bug
    def test_free_plan_tenant_omits_role(self):
        """Test that role field is omitted for free-plan tenants."""
        user = {
            "email": "alice@example.com",
            "display_name": "Alice Smith",
            "role": "admin",
        }
        result = build_user_create_payload(user, "free_tenant_123")
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
