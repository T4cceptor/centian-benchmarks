import unittest
from user_payload import build_user_create_payload

class RegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        user = {"email": "free@example.com", "display_name": "Free User", "role": "admin"}
        result = build_user_create_payload(user, "free_plan_123")
        self.assertNotIn("role", result["user"])
        
        # Test also when role is not provided
        user_no_role = {"email": "free2@example.com", "display_name": "Free User 2"}
        result2 = build_user_create_payload(user_no_role, "free_plan_456")
        self.assertNotIn("role", result2["user"])

if __name__ == "__main__":
    unittest.main()
