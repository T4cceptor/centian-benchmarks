import unittest

from user_payload import build_user_create_payload


class UserPayloadRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role_even_when_provided(self):
        user = {
            "email": "owner@example.com",
            "display_name": "Owner Name",
            "role": "admin",
        }

        result = build_user_create_payload(user, "free_team_123")

        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
