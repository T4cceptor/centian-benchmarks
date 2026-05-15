import unittest
from user_payload import build_user_create_payload

# TestRegression.test_free_plan_omits_role
class TestRegression(unittest.TestCase):
    def test_free_plan_omits_role(self):
        user = {"email": "free@example.com", "display_name": "Free User", "role": "admin"}
        tenant_id = "free_tenant_123"
        result = build_user_create_payload(user, tenant_id)
        
        # The 'role' field must be omitted for free-plan tenants.
        assert "role" not in result["user"], "'role' should not be in payload['user']"

if __name__ == "__main__":
    unittest.main()
