import unittest
from user_payload import build_user_create_payload

class TestRegression(unittest.TestCase):
    def test_free_plan_omits_role(self):
        user = {
            "email": "free@example.com",
            "display_name": "Free User",
            "role": "admin"
        }
        # Tenants starting with 'free_' are free-plan tenants.
        result = build_user_create_payload(user, "free_tenant_123")
        
        # Rule 2: The role field must be omitted from the payload for free-plan tenants.
        if "role" in result["user"]:
            raise AssertionError("'role' should not be in payload for free-plan tenants")


if __name__ == "__main__":
    unittest.main()
