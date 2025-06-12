import re
from datetime import datetime
from pydantic import BaseModel, field_validator
from src.services import is_car_number_not_unique


class CarAddSchema(BaseModel):
    car_number: str
    entry_at: datetime

    @field_validator("car_number")
    def validate_car_number(cls, number):
        number = number.upper()

        if is_car_number_not_unique(number):
            raise ValueError("Машина с таким номером уже находится на парковке")

        pattern = re.compile(r"^[АВЕКМНОРСТУХABEKMHOPCTYX]{1}\d{3}[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{2,3}$")
        if not pattern.match(number):
            raise ValueError("Некорректный формат автомобильного номера.")

        return number


class CarPaySchema(BaseModel):
    car_number: str
    payment_at: datetime

class CarExitSchema(BaseModel):
    car_number: str
    exit_at: datetime