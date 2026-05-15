import unittest
from user_payload import build_user_create_payload

class TestRegression(unittest.TestCase):
    def test_free_plan_user_has_no_role(self):
        user = {
            "email": "test@example.com",
            "display_name": "Test User",
            "role": "admin"
        }
        tenant_id = "free_123"
        payload = build_user_create_payload(user, tenant_id)
        
        self.assertNotIn("role", payload["user"])


if __name__ == "__main__":
    unittest.main()
