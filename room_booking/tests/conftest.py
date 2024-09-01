import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

api_client = APIClient()


@pytest.fixture
def user():
    """ объект user """
    return User.objects.create_user(username='testuser', password='testpassword')

