import unittest
from user_payload import build_user_create_payload

# TestRegression.test_free_plan_omits_role
class TestRegression(unittest.TestCase):
    def test_free_plan_omits_role(self):
        """Test that free-plan tenants omit the role field."""
        user = {"email": "free@example.com", "display_name": "Free User", "role": "admin"}
        result = build_user_create_payload(user, "free_tenant_123")
        self.assertFalse("role" in result["user"], "role field should be omitted for free tenants")

if __name__ == "__main__":
    unittest.main()
