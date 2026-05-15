import unittest

from user_payload import build_user_create_payload


class TestFreeplanRoleOmission(unittest.TestCase):
    def test_free_plan_omits_role(self):
        """For free-plan tenants, the role field must be completely omitted from the payload."""
        user = {
            "email": "alice@example.com",
            "display_name": "Alice",
            "role": "admin",
        }
        result = build_user_create_payload(user, "free_user_123")
        
        # The role field must not be present in the payload for free-plan tenants
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
