import unittest

from user_payload import build_user_create_payload


class FreePlanRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role_from_payload(self):
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_123")
        self.assertNotIn(
            "role",
            result["user"],
            "Free-plan tenants must not have a 'role' key in the user payload",
        )

    def test_free_plan_tenant_omits_role_even_when_caller_provides_role(self):
        user = {"email": "bob@example.com", "display_name": "Bob", "role": "admin"}
        result = build_user_create_payload(user, "free_trial_456")
        self.assertNotIn(
            "role",
            result["user"],
            "Free-plan tenants must discard any provided role",
        )


if __name__ == "__main__":
    unittest.main()
