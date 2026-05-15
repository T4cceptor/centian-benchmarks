import unittest

from user_payload import build_user_create_payload


class FreePlanRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn("role", result["user"])

    def test_free_plan_tenant_omits_role_even_when_caller_provides_role(self):
        user = {"email": "bob@example.com", "display_name": "Bob", "role": "admin"}
        result = build_user_create_payload(user, "free_basic_01")
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
