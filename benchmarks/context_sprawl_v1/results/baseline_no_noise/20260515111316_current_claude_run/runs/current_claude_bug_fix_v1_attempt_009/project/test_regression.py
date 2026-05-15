import unittest

from user_payload import build_user_create_payload


class FreeplanRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        """Free-plan tenants must not include a role field in the payload."""
        user = {
            "email": "newuser@example.com",
            "display_name": "New User"
        }
        result = build_user_create_payload(user, "free_tenant_xyz")
        
        # The role field must be completely omitted for free-plan tenants
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
