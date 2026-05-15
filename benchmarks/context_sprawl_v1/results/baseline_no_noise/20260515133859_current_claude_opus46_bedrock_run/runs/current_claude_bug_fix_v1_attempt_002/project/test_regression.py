import unittest

from user_payload import build_user_create_payload


class FreePlanRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role_from_payload(self):
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_org")
        self.assertNotIn(
            "role",
            result["user"],
            "Free-plan tenants must not include the 'role' key in the payload",
        )

    def test_free_plan_tenant_omits_role_even_when_caller_provides_one(self):
        user = {"email": "bob@example.com", "display_name": "Bob", "role": "admin"}
        result = build_user_create_payload(user, "free_trial_co")
        self.assertNotIn(
            "role",
            result["user"],
            "Free-plan tenants must discard any provided role",
        )


if __name__ == "__main__":
    unittest.main()
