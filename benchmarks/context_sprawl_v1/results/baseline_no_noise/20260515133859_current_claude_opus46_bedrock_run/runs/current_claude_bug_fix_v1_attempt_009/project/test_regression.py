import unittest

from user_payload import build_user_create_payload


class TestFreePlanRoleOmitted(unittest.TestCase):
    def test_free_plan_tenant_omits_role_from_payload(self):
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_starter_99")
        self.assertNotIn("role", result["user"])

    def test_free_plan_tenant_discards_explicit_role(self):
        user = {"email": "bob@example.com", "display_name": "Bob", "role": "admin"}
        result = build_user_create_payload(user, "free_team_5")
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
