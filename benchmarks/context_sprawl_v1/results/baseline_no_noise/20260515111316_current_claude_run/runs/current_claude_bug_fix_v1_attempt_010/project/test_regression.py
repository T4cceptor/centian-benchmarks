import unittest

from user_payload import build_user_create_payload


class UserPayloadRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role_field(self):
        """Free-plan tenants must not have a role field in the payload."""
        user = {"email": "test@example.com", "display_name": "Test User"}
        result = build_user_create_payload(user, "free_plan_tenant")
        
        # The role field must be completely omitted for free-plan tenants
        self.assertNotIn("role", result["user"])

    def test_free_plan_tenant_with_provided_role_still_omits_it(self):
        """Even if a role is provided, free-plan tenants must omit it."""
        user = {
            "email": "test@example.com",
            "display_name": "Test User",
            "role": "admin",
        }
        result = build_user_create_payload(user, "free_plan_tenant")
        
        # The role field must be omitted even if provided
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
