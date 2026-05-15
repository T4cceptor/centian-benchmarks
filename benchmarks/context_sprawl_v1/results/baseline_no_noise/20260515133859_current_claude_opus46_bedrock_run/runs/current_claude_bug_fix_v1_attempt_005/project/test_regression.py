import unittest

from user_payload import build_user_create_payload


class TestFreePlanRoleBug(unittest.TestCase):
    def test_free_plan_tenant_omits_role_from_payload(self):
        user = {"email": "newuser@example.com", "display_name": "New User"}
        result = build_user_create_payload(user, "free_starter_123")
        self.assertNotIn(
            "role",
            result["user"],
            "Free-plan tenants must not have 'role' in the user payload",
        )

    def test_free_plan_tenant_omits_role_even_when_provided(self):
        user = {
            "email": "another@example.com",
            "display_name": "Another User",
            "role": "admin",
        }
        result = build_user_create_payload(user, "free_org_456")
        self.assertNotIn(
            "role",
            result["user"],
            "Free-plan tenants must discard any provided role",
        )


if __name__ == "__main__":
    unittest.main()
