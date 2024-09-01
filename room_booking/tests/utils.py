import datetime as dt
from typing import Union

from room_booking import models


def validate_dict_fields(result: dict, valid_data: Union[tuple, list]):
    """ Валидация полей json """
    for row in valid_data:
        field_name = row[0]
        assert field_name in result, f'Field "{field_name}" not in result'
        if len(row) > 1:
            validator = row[1]
            if callable(validator):
                assert validator(result[field_name])
            else:
                assert validator == result[
                    field_name], f'{field_name} \nExpected: {validator}\nActual: {result[field_name]}'


def validate_rooms_reserves(obj_dict, instanse: models.Reserve):
    start_time = dt.datetime.strftime(instanse.start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    end_time = dt.datetime.strftime(instanse.start_time, '%Y-%m-%dT%H:%M:%S.%fZ')