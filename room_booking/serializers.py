import datetime as dt
from typing import Optional

import pytz
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from room_booking import models, utils


class CreateReserveSerializer(serializers.ModelSerializer):
    """ Сериализация бронирования комнаты """
    room = serializers.CharField(required=True, max_length=256)

    class Meta:
        model = models.Reserve
        fields = ('id', 'room', 'start_time', 'end_time', 'description')

    def validate_room(self, room: str) -> Optional[models.Room]:
        """ Проверка наличия комнаты """
        if room:
            return utils.get_object_by_name(room, key='Room')

        return None

    def validate(self, data):
        """ Валидация по времени бронирования """
        start_time = data['start_time']
        end_time = data['end_time']
        room = utils.get_object_by_name(data['room'], key='Room')
        if end_time < start_time:
            raise ValidationError('end_time must be bigger than start_time')
        if start_time < dt.datetime.now(tz=pytz.UTC):
            raise ValidationError('You cannot reserve room for past time')
        if _get_room_status(room, start_time, end_time):
            raise ValidationError('Room already reserved on this time')
        return data


class ReservesSerializer(serializers.ModelSerializer):
    """ Сериализация брони комнаты """
    reserved_by = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = models.Reserve
        fields = ('reserved_by', 'start_time', 'end_time', 'description')


class RoomSerializer(serializers.ModelSerializer):
    """ Сериализация комнаты """
    room_reserves = serializers.SerializerMethodField()
    is_free = serializers.SerializerMethodField()

    class Meta:
        model = models.Room
        fields = ('name', 'is_free', 'room_reserves')

    def get_is_free(self, instance: models.Room) -> bool:
        """ Статус комнаты в текущий момент. Свободна или нет """
        return not models.Reserve.objects.filter(
            Q(room=instance) & Q(start_time__lte=dt.datetime.now()) & Q(end_time__gte=dt.datetime.now())).exists()

    def get_room_reserves(self, instance: models.Room):
        start_date = self.context.get('start_date')
        end_date = self.context.get('end_date')

        if start_date > end_date:
            raise ValidationError('Start date must be lower than end date')
        filter_context = {'start_time__gte': start_date, 'end_time__lte': end_date}
        reserves = instance.room_reserves.filter(**filter_context).select_related('reserved_by')
        return ReservesSerializer(reserves, many=True, read_only=True).data


def _get_room_status(obj: models.Room, first_date: dt.datetime, second_date: dt.datetime) -> bool:
    intersection_by_start_date = Q(start_time__gt=first_date) & Q(end_time__lt=first_date)
    intersection_by_end_date = Q(start_time__gt=second_date) & Q(end_time__lt=second_date)
    external_intersection = Q(start_time__lte=first_date) & Q(end_time__gte=second_date)
    internal_intersection = Q(start_time__gte=first_date) & Q(end_time__lte=second_date)

    return models.Reserve.objects.filter(
        Q(room=obj) & (
                intersection_by_start_date | intersection_by_end_date | external_intersection | internal_intersection)).exists()
