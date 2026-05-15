import unittest

from user_payload import build_user_create_payload


class FreeplanUserPayloadTests(unittest.TestCase):
    def test_free_plan_tenant_omits_role_field(self):
        """Free-plan tenants must not include role field in payload.
        
        The role field must be completely omitted (not set to null, not set to
        any default value) for free-plan tenants (tenant_id starting with
        'free_'). This is required by the MyOrgAPI specification.
        """
        user = {"email": "alice@example.com", "display_name": "Alice"}
        result = build_user_create_payload(user, "free_plan_tenant")
        
        # The role field must not be present at all
        self.assertNotIn("role", result["user"])


if __name__ == "__main__":
    unittest.main()
