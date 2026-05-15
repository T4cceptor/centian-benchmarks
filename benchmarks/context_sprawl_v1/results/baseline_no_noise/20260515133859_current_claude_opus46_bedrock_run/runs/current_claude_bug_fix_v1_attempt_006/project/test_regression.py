import unittest

from user_payload import build_user_create_payload


class TestFreePlanRoleBug(unittest.TestCase):
    def test_free_plan_tenant_omits_role_from_payload(self):
        user = {"email": "newuser@example.com", "display_name": "New User"}
        result = build_user_create_payload(user, "free_starter_123")
        self.assertNotIn("role", result["user"])

    def test_free_plan_tenant_discards_explicit_role(self):
        user = {
            "email": "admin@example.com",
            "display_name": "Admin User",
            "role": "admin",
        }
        result = build_user_create_payload(user, "free_starter_123")
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
