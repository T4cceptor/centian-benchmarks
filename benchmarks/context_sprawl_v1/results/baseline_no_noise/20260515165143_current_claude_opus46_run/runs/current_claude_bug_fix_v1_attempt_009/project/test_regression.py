import unittest

from user_payload import build_user_create_payload


class FreePlanRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        """Free-plan tenants (tenant_id starting with 'free_') must not have
        the 'role' key in the user dict at all — the API rejects it with 400."""
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_123")
        self.assertNotIn(
            "role",
            result["user"],
            "Payload for free-plan tenant must omit the 'role' key entirely",
        )

    def test_free_plan_tenant_omits_role_even_when_caller_provides_one(self):
        """Even if the caller explicitly passes a role, it must be discarded
        for free-plan tenants."""
        user = {
            "email": "bob@example.com",
            "display_name": "Bob",
            "role": "admin",
        }
        result = build_user_create_payload(user, "free_starter_456")
        self.assertNotIn(
            "role",
            result["user"],
            "Provided role must be discarded for free-plan tenants",
        )


if __name__ == "__main__":
    unittest.main()
