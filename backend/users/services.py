from rest_framework_simplejwt.tokens import RefreshToken


def create_token_pair(user):
    """Create the token response shared by registration and login."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
