import unittest

from user_payload import build_user_create_payload


class TestFreeplanRoleOmitted(unittest.TestCase):
    def test_free_plan_tenant_omits_role_field(self):
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_123")
        self.assertNotIn("role", result["user"])

    def test_free_plan_tenant_omits_role_even_when_provided(self):
        user = {"email": "bob@example.com", "display_name": "Bob", "role": "admin"}
        result = build_user_create_payload(user, "free_hobby_456")
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
