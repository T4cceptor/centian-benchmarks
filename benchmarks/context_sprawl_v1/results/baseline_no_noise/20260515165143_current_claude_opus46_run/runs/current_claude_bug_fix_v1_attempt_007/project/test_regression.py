import unittest

from user_payload import build_user_create_payload


class FreePlanRegressionTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role(self):
        """Free-plan tenants (tenant_id starting with 'free_') must not have
        a 'role' key in the user dict at all — the API returns 400 otherwise."""
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn(
            "role",
            result["user"],
            "role key must be omitted for free-plan tenants",
        )

    def test_free_plan_tenant_discards_explicit_role(self):
        """Even if the caller provides a role, it must be discarded for
        free-plan tenants."""
        user = {"email": "bob@example.com", "display_name": "Bob", "role": "admin"}
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn(
            "role",
            result["user"],
            "explicit role must be discarded for free-plan tenants",
        )


if __name__ == "__main__":
    unittest.main()
