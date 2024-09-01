from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Room(models.Model):
    """ Переговорная комната """
    name = models.CharField(max_length=32, verbose_name='Наименование комнаты', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'


class Reserve(models.Model):
    """ Бронь комнаты """
    room = models.ForeignKey(Room, null=False, blank=False, on_delete=models.CASCADE,
                             related_name='room_reserves', verbose_name='Забронированная комната')

    reserved_by = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE,
                                    related_name='user_reserves', verbose_name='Бронирующий')

    start_time = models.DateTimeField(null=False, blank=False, verbose_name='Время начала')
    end_time = models.DateTimeField(null=False, blank=False, verbose_name='Время окончания')

    description = models.TextField(max_length=512, verbose_name='Цель бронирования')

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Бронирования'
