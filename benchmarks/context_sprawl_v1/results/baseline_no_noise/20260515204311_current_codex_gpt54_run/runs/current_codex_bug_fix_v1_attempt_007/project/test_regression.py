import unittest

from user_payload import build_user_create_payload


class FreePlanUserPayloadRegressionTests(unittest.TestCase):
    # Planned regression entrypoint: FreePlanUserPayloadRegressionTests.test_free_plan_tenant_omits_role_even_when_provided
    def test_free_plan_tenant_omits_role_even_when_provided(self):
        user = {
            "email": "Admin@Example.COM",
            "display_name": "  Admin   User  ",
            "role": "admin",
        }

        result = build_user_create_payload(user, "free_team_123")

        self.assertEqual(result["user"]["email"], "admin@example.com")
        self.assertEqual(result["user"]["display_name"], "Admin User")
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
