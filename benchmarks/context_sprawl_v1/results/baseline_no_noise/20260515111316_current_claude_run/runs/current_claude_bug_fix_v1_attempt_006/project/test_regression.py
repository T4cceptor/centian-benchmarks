import unittest

from user_payload import build_user_create_payload


class TestFreeplanRoleOmission(unittest.TestCase):
    def test_free_plan_omits_role_field(self):
        """Free-plan tenants must not have role field in payload."""
        user = {"email": "test@example.com", "display_name": "Test User"}
        result = build_user_create_payload(user, "free_plan_tenant")
        
        # The role field must be completely omitted, not just set to a default
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
