import unittest

from user_payload import build_user_create_payload


class FreePlanRoleRegressionTests(unittest.TestCase):
    """Regression coverage for FreePlanRoleRegressionTests.test_free_plan_omits_role_when_role_provided."""
    def test_free_plan_omits_role_when_role_provided(self):
        user = {
            "email": "paid.user@example.com",
            "display_name": "Paid User",
            "role": "admin",
        }

        result = build_user_create_payload(user, "free_team_123")

        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
