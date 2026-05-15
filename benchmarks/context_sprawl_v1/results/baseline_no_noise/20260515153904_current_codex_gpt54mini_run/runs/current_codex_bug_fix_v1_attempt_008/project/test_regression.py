import unittest

from user_payload import build_user_create_payload


class RegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        user = {
            "email": "owner@example.com",
            "display_name": "  Owner   Name  ",
            "role": "admin",
        }

        result = build_user_create_payload(user, "free_team_123")

        self.assertNotIn("role", result["user"])
        self.assertEqual(result["user"]["email"], "owner@example.com")
        self.assertEqual(result["user"]["display_name"], "Owner Name")
        self.assertEqual(result["metadata"]["version"], 2)


if __name__ == "__main__":
    unittest.main()
