import unittest
from user_payload import build_user_create_payload

class TestRegression(unittest.TestCase):
    def test_free_plan_omits_role(self):
        user = {"email": "free@example.com", "display_name": "Free User"}
        result = build_user_create_payload(user, "free_tenant_123")
        if "role" in result["user"]:
            raise AssertionError("'role' unexpectedly found in user payload")


if __name__ == "__main__":
    unittest.main()
