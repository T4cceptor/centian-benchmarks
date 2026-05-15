import unittest

from user_payload import build_user_create_payload

class RegressionTests(unittest.TestCase):
    def test_free_plan_omits_role(self):
        user = {"email": "free@example.com", "display_name": "Free User", "role": "admin"}
        result = build_user_create_payload(user, "free_tenant_1")
        self.assertNotIn("role", result["user"])
        
    def test_free_plan_omits_role_even_if_not_provided(self):
        user = {"email": "free2@example.com", "display_name": "Free User 2"}
        result = build_user_create_payload(user, "free_tenant_2")
        self.assertNotIn("role", result["user"])

if __name__ == "__main__":
    unittest.main()
