from rest_framework.permissions import IsAuthenticated


class AuthenticationMixin:
    """ Миксин authentication_classes """
    permission_classes = (IsAuthenticated,)
