import unittest

from user_payload import build_user_create_payload


class UserPayloadTests(unittest.TestCase):
    def test_basic_payload_lowercases_email(self):
        user = {"email": "Alice@Example.COM", "display_name": "Alice"}
        result = build_user_create_payload(user, "tenant_abc")
        self.assertEqual(result["user"]["email"], "alice@example.com")

    def test_display_name_whitespace_is_normalized(self):
        user = {"email": "bob@example.com", "display_name": "  Bob   Smith  "}
        result = build_user_create_payload(user, "tenant_abc")
        self.assertEqual(result["user"]["display_name"], "Bob Smith")

    def test_legacy_tenant_preserves_email_casing(self):
        user = {"email": "Carol@Example.COM", "display_name": "Carol"}
        result = build_user_create_payload(user, "legacy_corp_42")
        self.assertEqual(result["user"]["email"], "Carol@Example.COM")

    def test_archive_tenant_uses_v1_metadata(self):
        user = {"email": "dave@example.com", "display_name": "Dave"}
        result = build_user_create_payload(user, "archive_old_inc")
        self.assertEqual(result["metadata"]["version"], 1)

    def test_default_metadata_version_is_2(self):
        user = {"email": "eve@example.com", "display_name": "Eve"}
        result = build_user_create_payload(user, "tenant_xyz")
        self.assertEqual(result["metadata"]["version"], 2)

    def test_role_defaults_to_member_when_not_specified(self):
        user = {"email": "frank@example.com", "display_name": "Frank"}
        result = build_user_create_payload(user, "tenant_xyz")
        self.assertEqual(result["user"]["role"], "member")

    def test_explicit_role_is_preserved(self):
        user = {
            "email": "grace@example.com",
            "display_name": "Grace",
            "role": "admin",
        }
        result = build_user_create_payload(user, "tenant_xyz")
        self.assertEqual(result["user"]["role"], "admin")


if __name__ == "__main__":
    unittest.main()
