import unittest

from user_payload import build_user_create_payload

# Test: FreeplanRegressionTests.test_free_plan_omits_role


class FreeplanRegressionTests(unittest.TestCase):
    def test_free_plan_omits_role(self):
        """Free-plan tenants must have role field completely omitted from payload."""
        user = {
            "email": "test@example.com",
            "display_name": "Test User",
            "role": "admin",  # Role provided by caller, but should be omitted
        }
        result = build_user_create_payload(user, "free_tenant_123")
        
        # The role field must not be present in the user object at all
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
