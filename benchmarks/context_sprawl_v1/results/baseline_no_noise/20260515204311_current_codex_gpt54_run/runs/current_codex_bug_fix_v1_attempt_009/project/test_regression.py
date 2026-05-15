import unittest

from user_payload import build_user_create_payload


class FreePlanUserPayloadRegressionTests(unittest.TestCase):
    # FreePlanUserPayloadRegressionTests.test_free_plan_omits_role_even_when_provided
    def test_free_plan_omits_role_even_when_provided(self):
        user = {
            "email": "new.user@example.com",
            "display_name": "  New   User  ",
            "role": "admin",
        }

        result = build_user_create_payload(user, "free_tenant_123")

        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
