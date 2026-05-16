from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


class RegistrationRateThrottle(AnonRateThrottle):
    scope = "registration"


class ActivationRateThrottle(AnonRateThrottle):
    scope = "activation"


class PasswordResetRateThrottle(AnonRateThrottle):
    scope = "password_reset"
