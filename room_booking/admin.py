from django.contrib import admin

from room_booking import models


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):
    """ Админка для Poll """
    list_display = ('name',)
    search_fields = ('name',)
