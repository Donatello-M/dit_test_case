import datetime as dt

from rest_framework.exceptions import NotFound

from room_booking import models


def get_object_by_name(name: str, key: str) -> models.Room:
    try:
        obj = getattr(models, key).objects.get(name=name)
    except getattr(models, key).DoesNotExist as ex:
        raise NotFound({'detail': f'{key} <{name}> not found.'}) from ex
    return obj


def get_filter_params(request):
    start_date = request.query_params.get('start_date', str(
        dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)))
    end_date = request.query_params.get('end_date', str(
        dt.datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)))

    return start_date, end_date
