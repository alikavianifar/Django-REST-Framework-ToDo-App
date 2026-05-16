from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """One-time, user-scoped activation token (not a JWT)."""

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.email}{timestamp}{user.is_verified}"


account_activation_token = AccountActivationTokenGenerator()

# Django default generator for password reset (invalidates when password changes).
password_reset_token = PasswordResetTokenGenerator()
