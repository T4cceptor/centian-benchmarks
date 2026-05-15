import unittest
from user_payload import build_user_create_payload

class RegressionTests(unittest.TestCase):
    def test_free_plan_omits_role(self):
        user = {"email": "test@example.com", "display_name": "Test User", "role": "admin"}
        result = build_user_create_payload(user, "free_tenant_1")
        self.assertNotIn("role", result["user"])

if __name__ == "__main__":
    unittest.main()
