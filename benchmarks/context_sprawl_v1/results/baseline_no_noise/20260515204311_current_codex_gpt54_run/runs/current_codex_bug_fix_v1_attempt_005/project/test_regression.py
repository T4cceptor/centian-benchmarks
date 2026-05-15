import unittest

from user_payload import build_user_create_payload


class FreePlanRoleRegressionTests(unittest.TestCase):
    def test_free_plan_omits_role_even_when_provided(self):
        user = {
            "email": "PaidAdmin@Example.COM",
            "display_name": "  Paid   Admin  ",
            "role": "admin",
        }

        result = build_user_create_payload(user, "free_team_123")

        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
