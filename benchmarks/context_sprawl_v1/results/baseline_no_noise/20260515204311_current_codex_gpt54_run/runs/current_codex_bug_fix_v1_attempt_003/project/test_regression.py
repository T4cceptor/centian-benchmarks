import unittest

from user_payload import build_user_create_payload


class FreePlanRoleRegressionTests(unittest.TestCase):
    # Planned test: FreePlanRoleRegressionTests.test_free_plan_omits_role_even_when_provided
    def test_free_plan_omits_role_even_when_provided(self):
        user = {
            "email": "free.user@example.com",
            "display_name": "Free User",
            "role": "admin",
        }

        result = build_user_create_payload(user, "free_tenant_123")

        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
