from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountDeleteTokenGenerator(PasswordResetTokenGenerator):
    """
    # Override this method  to remove the user `last_login` value from the hash.
        # As this token is used for deleting the user, so there is no worry
        # that the token will be used again.
    """
    def _make_hash_value(self, user, timestamp):

        email_field = user.get_email_field_name()
        email = getattr(user, email_field, "") or ""
        return f"{user.pk}{user.password}{timestamp}{email}"


account_delete_token_generator = AccountDeleteTokenGenerator()
