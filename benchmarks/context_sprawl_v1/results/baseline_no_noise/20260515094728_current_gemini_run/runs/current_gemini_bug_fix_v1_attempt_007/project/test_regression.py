import unittest
from user_payload import build_user_create_payload

class TestRegression(unittest.TestCase):
    def test_free_plan_user_role_omitted(self):
        user = {
            "email": "USER@example.com",
            "display_name": "Test User",
            "role": "admin"
        }
        tenant_id = "free_123"
        payload = build_user_create_payload(user, tenant_id)
        
        self.assertNotIn("role", payload["user"], "Role should be omitted for free-plan tenants")

if __name__ == "__main__":
    unittest.main()
