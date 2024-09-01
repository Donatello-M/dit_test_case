import datetime as dt
from unittest.mock import ANY

import pytest
from django.contrib.auth import get_user_model
from django.db.models import Q

from django.urls import reverse
from pytz import UTC
from rest_framework.test import APIClient

from room_booking.tests import utils
from room_booking import models

pytestmark = pytest.mark.django_db(['default'])

api_client = APIClient()

User = get_user_model()


def test_get_room_schedule(user):
    """ Получение расписания комнаты. Без фильтров возвращается расписание за сегодня """
    token = _get_token(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    room = _create_room_with_reserves()  # Cоздаст 2 брони на текущую дату
    endpoint = reverse('room-schedule', kwargs={'room_name': room.name})
    response = api_client.get(endpoint)
    response_json = response.json()

    is_free = not models.Reserve.objects.filter(
            Q(room=room) & Q(start_time__lte=dt.datetime.now()) & Q(end_time__gte=dt.datetime.now())).exists()

    assert response.status_code == 200
    utils.validate_dict_fields(response_json, (
        ('name', room.name),
        ('is_free', is_free),
        ('room_reserves', ANY)
    ))
    assert len(response_json['room_reserves']) == 2


def test_get_room_schedule_with_filter_parameter(user):
    """ Получение расписания комнаты за период """
    token = _get_token(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    start_date = '2024-11-5 00:00:00Z'
    end_date = '2024-11-6 00:00:00Z'

    room = _create_room_with_reserves()  # Cоздаст 1 бронь в промежутке между start_date и end_date
    endpoint = reverse('room-schedule',
                       kwargs={'room_name': room.name}) + f'?start_date={start_date}&end_date={end_date}'
    response = api_client.get(endpoint)
    response_json = response.json()

    is_free = not models.Reserve.objects.filter(
        Q(room=room) & Q(start_time__lte=dt.datetime.now()) & Q(end_time__gte=dt.datetime.now())).exists()

    assert response.status_code == 200
    utils.validate_dict_fields(response_json, (
        ('name', room.name),
        ('is_free', is_free),
        ('room_reserves', ANY)
    ))
    assert len(response_json['room_reserves']) == 1


def test_create_reserve(user):
    """ Бронирование комнаты """
    token = _get_token(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    room = _create_room_with_reserves()
    endpoint = reverse('room-booking')

    start_time = '2024-09-13 09:00:00Z'
    end_time = '2024-09-13 10:00:00Z'

    request_data = {'room': room.name, 'start_time': str(start_time), 'end_time': str(end_time),
                    'description': 'description'}
    response = api_client.post(endpoint, data=request_data)
    response_json = response.json()

    reserve = models.Reserve.objects.get(pk=response_json['id'])
    start_time = dt.datetime.strftime(reserve.start_time, '%Y-%m-%dT%H:%M:%SZ')
    end_time = dt.datetime.strftime(reserve.end_time, '%Y-%m-%dT%H:%M:%SZ')
    assert response.status_code == 201
    utils.validate_dict_fields(response.json(), (
        ('room', reserve.room.name),
        ('description', reserve.description),
        ('start_time', start_time),
        ('end_time', end_time)
    ))


@pytest.mark.parametrize('start_time, end_time', [('2024-09-13 10:00:00Z', '2024-05-13 09:00:00Z'),
                                                  ('2022-09-13 10:00:00Z', '2022-09-13 11:00:00Z')])
def test_validate_by_dates(user, start_time, end_time):
    """ Валидация по датам при бронировании комнаты """
    token = _get_token(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    room = _create_room_with_reserves()
    endpoint = reverse('room-booking')
    request_data = {'room': room.name, 'start_time': start_time, 'end_time': end_time,
                    'description': 'description'}
    response = api_client.post(endpoint, data=request_data)
    assert response.status_code == 400


def test_get_400_on_occupied_room_reserve(user):
    """ Попытка забронировать комнату на время существующей брони """
    test_create_reserve(user)
    token = _get_token(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    start_time = '2024-09-13 09:00:00Z'
    end_time = '2024-09-13 10:00:00Z'

    endpoint = reverse('room-booking')

    room = models.Room.objects.all().first()
    request_data = {'room': room.name, 'start_time': start_time, 'end_time': end_time,
                    'description': 'description'}
    response = api_client.post(endpoint, data=request_data)
    assert response.status_code == 400


def test_get_404_with_non_existent_room(user):
    """ 404 статус при запросе расписания на несуществующую комнату """
    token = _get_token(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    endpoint = reverse('room-schedule', kwargs={'room_name': 'unknown_room'})
    response = api_client.get(endpoint)

    assert response.status_code == 404


def test_post_404_with_non_existent_room(user):
    """ 404 статус при создании брони на несуществующую комнату """
    token = _get_token(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    endpoint = reverse('room-booking')
    start_time = '2024-09-13 09:00:00Z'
    end_time = '2024-09-13 10:00:00Z'

    request_data = {'room': 'unknown_room', 'start_time': str(start_time), 'end_time': str(end_time),
                    'description': 'description'}

    response = api_client.post(endpoint, data=request_data)

    assert response.status_code == 404


def test_get_401_unauthorized_request():
    """ 401 статус при неавторизованном запросе на ручку расписаний """
    endpoint = reverse('room-schedule', kwargs={'room_name': 'unknown_room'})
    response = api_client.get(endpoint)

    assert response.status_code == 401


def test_post_401_unauthorized_request():
    """ 401 статус при неавторизованном запросе на ручку бронирования """
    endpoint = reverse('room-booking')
    start_time = '2024-09-13 09:00:00Z'
    end_time = '2024-09-13 10:00:00Z'

    request_data = {'room': 'unknown_room', 'start_time': str(start_time), 'end_time': str(end_time),
                    'description': 'description'}

    response = api_client.post(endpoint, data=request_data)

    assert response.status_code == 401


@pytest.mark.parametrize('endpoint', ['room-report-list', 'room-report-retrieve'])
def test_get_report(user, endpoint):
    room = _create_room_with_reserves()
    token = _get_token(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    kwargs = {'room_name': room.name} if endpoint == 'room-report-retrieve' else {}
    url = reverse(endpoint, kwargs=kwargs)
    data = {'start_date': '2024-11-5 00:00:00Z', 'end_date': '2024-09-13 10:00:00Z'}
    response = api_client.get(url, data=data)
    assert response.status_code == 200

    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


def _get_token(user: User) -> str:
    response = api_client.post('/api/auth/jwt/create/', {
        'username': user.username,
        'password': 'testpassword'
    })
    assert response.status_code == 200

    return response.data['access']


def _create_room_with_reserves() -> models.Room:
    user = User.objects.create_user(username='user', password='password')

    room = models.Room.objects.create(name='room')

    reserve_1 = models.Reserve(start_time=dt.datetime.now(tz=UTC).replace(hour=12),
                               end_time=dt.datetime.now(tz=UTC).replace(hour=13), reserved_by=user, room=room)
    reserve_2 = models.Reserve(start_time=dt.datetime.now(tz=UTC).replace(hour=15),
                               end_time=dt.datetime.now(tz=UTC).replace(hour=18), reserved_by=user, room=room)
    reserve_3 = models.Reserve(start_time=dt.datetime(2024, 11, 5, 11, 0, 0, tzinfo=UTC),
                               end_time=dt.datetime(2024, 11, 5, 12, 0, 0, tzinfo=UTC), reserved_by=user, room=room)

    models.Reserve.objects.bulk_create([reserve_1, reserve_2, reserve_3])

    return room
