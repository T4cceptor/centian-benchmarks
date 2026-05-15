import unittest
from user_payload import build_user_create_payload

class TestRegression(unittest.TestCase):
    def test_role_is_omitted_for_free_tenants(self):
        user = {"email": "free@example.com", "display_name": "Free User", "role": "admin"}
        tenant_id = "free_tenant_123"
        result = build_user_create_payload(user, tenant_id)
        
        # Ensure the error message is exactly what is expected in planning
        if "role" in result["user"]:
            raise AssertionError("'role' should not be in payload for free-plan tenants")

if __name__ == "__main__":
    unittest.main()
