from src.schemas import CarAddSchema, CarPaySchema, CarExitSchema
from src.services import add_car_to_db, add_payment_time, exit_parking
from fastapi import APIRouter


router = APIRouter()

@router.post("/entry")
def entry_to_parking(data: CarAddSchema):
    add_car_to_db(data)
    return {'message': 'Шлагбаум открыт. Парковка до 1 часа бесплатна. Больше 1 часа - 100р. Больше 2ух часов - 150р за каждый час.'}


@router.post("/payment")
def payment_for_parking(data: CarPaySchema):
    add_payment_time(data)
    return {'message': 'Оплата произведена. У вас есть 5 минут, чтобы выехать с парковки. Удачного пути!'}


@router.post("/exit")
def exit_the_parking(data: CarExitSchema):
    car_number = data.car_number
    exit_at = data.exit_at.replace(tzinfo=None)
    result = exit_parking(exit_at, car_number)
    return {'message': f'{result}'}