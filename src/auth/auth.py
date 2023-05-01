from fastapi_users.authentication import CookieTransport, BearerTransport
from fastapi_users.authentication import JWTStrategy
from fastapi_users.authentication import AuthenticationBackend

#cookie_transport = CookieTransport(cookie_name='imagehost', cookie_max_age=3600)
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

SECRET = "SECRET"


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=36000)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)