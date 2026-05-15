import unittest
from user_payload import build_user_create_payload

class RegressionTests(unittest.TestCase):
    def test_free_plan_omits_role(self):
        user = {"email": "free@example.com", "display_name": "Free User"}
        result = build_user_create_payload(user, "free_tenant_123")
        self.assertNotIn("role", result["user"], msg="AssertionError: 'role' should be omitted for free-plan tenants")

if __name__ == "__main__":
    unittest.main()
