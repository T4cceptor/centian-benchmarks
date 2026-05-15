import unittest

from user_payload import build_user_create_payload


class FreePlanUserPayloadRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        user = {
            "email": "newuser@example.com",
            "display_name": "New User",
            "role": "admin",
        }

        result = build_user_create_payload(user, "free_team_123")

        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
