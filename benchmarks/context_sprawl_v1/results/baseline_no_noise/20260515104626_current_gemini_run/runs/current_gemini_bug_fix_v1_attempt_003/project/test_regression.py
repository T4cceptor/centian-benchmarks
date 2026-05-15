import unittest
from user_payload import build_user_create_payload

class TestRegression(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        user = {"email": "free@example.com", "display_name": "Free User"}
        # Free-plan tenants start with "free_"
        result = build_user_create_payload(user, "free_tenant_123")
        
        self.assertNotIn("role", result["user"], f"'role' unexpectedly found in {result['user']}")


if __name__ == "__main__":
    unittest.main()
