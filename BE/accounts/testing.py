from django.conf import settings
from .tokens import issue_token


def authenticate_client(client, user):
    token, _ = issue_token(user)
    client.cookies[settings.JWT_COOKIE_NAME] = token
