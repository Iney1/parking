from sqlalchemy import select, update
from sqlalchemy.orm import Session
from src.models import CarModel
from src.engine import engine


# Валидаторы Pyndaitc:

def is_car_number_not_unique(car_number):
    with Session(engine) as session:
        stmt = select(CarModel.car_number).where(CarModel.is_gone.is_not(True))
        car_numbers = session.execute(stmt).scalars().all()
        if car_number in car_numbers:
            return True


# Эндпоинты

# '/entry'
def add_car_to_db(data):
    new_car = CarModel(
        car_number=data.car_number,
        entry_at=data.entry_at,
    )
    with Session(engine) as session:
        session.add(new_car)
        session.commit()


# '/payment'
def add_payment_time(data):
    stmt = (update(CarModel).where(CarModel.car_number == data.car_number).where(CarModel.is_gone.is_not(True)).values(payment_at=data.payment_at))
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()


####### '/exit'

def is_already_payed(car_number):
    with Session(engine) as session:
        stmt = select(CarModel.payment_at).where(CarModel.is_gone.is_not(True)).where(CarModel.car_number == car_number)
        payment_at = session.scalar(stmt)
    if not payment_at:
        return False
    else:
        return True


def five_min_is_gone(exit_at, car_number):
    with Session(engine) as session:
        stmt = select(CarModel.payment_at).where(CarModel.is_gone.is_not(True)).where(CarModel.car_number == car_number)
        payment_at = session.scalar(stmt)
    minutes = (exit_at - payment_at).total_seconds() // 60
    return minutes < 5


def get_entry_time(car_number):
    with Session(engine) as session:
        stmt = select(CarModel.entry_at).where(CarModel.is_gone.is_not(True)).where(CarModel.car_number == car_number)
        entry_at = session.scalar(stmt).replace(tzinfo=None)
    return entry_at


def get_price(exit_at, entry_at):
    hours = (exit_at - entry_at).total_seconds() // 3600

    if hours <= 1:
        return 0
    elif hours < 2:
        return 100
    else:
        return hours * 150


def add_is_gone(car_number):
    stmt = (update(CarModel).where(CarModel.car_number == car_number).values(is_gone=True))
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()

def add_exit_at(car_number, exit_at):
    stmt = (update(CarModel).where(CarModel.is_gone.is_not(True)).where(CarModel.car_number == car_number).values(exit_at=exit_at))
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()


def exit_parking(exit_at, car_number):
    if is_already_payed(car_number):
        if five_min_is_gone(exit_at, car_number):
            add_is_gone(car_number)
            add_exit_at(car_number, exit_at)
            return 'Выезд разрешён. Доброго пути!'
        else:
            return 'К сожалению, вы не уложились в 5 минут. Выезд запрещён'
    else:
        entry_at = get_entry_time(car_number)
        price = get_price(exit_at, entry_at)
        if price > 0:
            return f'Пожалуйста, вернитесь и оплатите {price} рублей за парковку.'
        else:
            add_is_gone(car_number)
            add_exit_at(car_number, exit_at)
            return 'Выезд разрешён. Доброго пути!'