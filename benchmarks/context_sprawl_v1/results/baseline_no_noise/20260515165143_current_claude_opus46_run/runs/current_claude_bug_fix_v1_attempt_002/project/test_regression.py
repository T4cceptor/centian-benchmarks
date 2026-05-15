import unittest

from user_payload import build_user_create_payload


class FreePlanRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        """Free-plan tenants (tenant_id starting with 'free_') must not
        have a 'role' key in the user dict — not even set to None."""
        user = {"email": "newuser@example.com", "display_name": "New User"}
        result = build_user_create_payload(user, "free_starter_org")
        self.assertNotIn(
            "role",
            result["user"],
            "role must be omitted entirely for free-plan tenants",
        )

    def test_free_plan_tenant_omits_role_even_when_caller_provides_one(self):
        """Even if the caller passes a role, it must be discarded for free-plan tenants."""
        user = {
            "email": "admin@example.com",
            "display_name": "Admin",
            "role": "admin",
        }
        result = build_user_create_payload(user, "free_starter_org")
        self.assertNotIn(
            "role",
            result["user"],
            "provided role must be discarded for free-plan tenants",
        )


if __name__ == "__main__":
    unittest.main()
