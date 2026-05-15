import unittest
from user_payload import build_user_create_payload

class TestRegression(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        """Rule: The role field must be omitted from the payload for free-plan tenants."""
        user = {"email": "free@example.com", "display_name": "Free User", "role": "admin"}
        tenant_id = "free_tenant_123"
        result = build_user_create_payload(user, tenant_id)
        
        # Adjusting assertion to match the expectedError parameter in planning
        if "role" in result["user"]:
            raise AssertionError("AssertionError: 'role' in payload['user']")

if __name__ == "__main__":
    unittest.main()
