import re
from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

app = FastAPI()

engine = create_engine('sqlite:///parking.db')


@app.post('/setup_database')
def setup_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return {"message": "Создание/пересоздание базы прошло успешно"}


class CarAddSchema(BaseModel):
    car_number: str
    entry_at: datetime

    @field_validator("car_number")
    def validate_car_number(cls, number):
        number = number.upper()

        with Session(engine) as session:
            stmt = select(CarModel.car_number)
            car_numbers = session.execute(stmt).scalars().all()
            if number in car_numbers:
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

@app.post("/entry")
def entry_to_parking(data: CarAddSchema):
    new_car = CarModel(
        car_number=data.car_number,
        entry_at=data.entry_at,
    )
    with Session(engine) as session:
        session.add(new_car)
        session.commit()
    return {'message': 'Шлагбаум открыт. Парковка до 1 часа бесплатна. Больше 1 часа - 100р. Больше 2ух часов - 150р за каждый час.'}


@app.post("/payment")
def payment_for_parking(data: CarPaySchema):
    stmt = (update(CarModel).where(CarModel.car_number == data.car_number).values(payment_at=data.payment_at)
    )
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()
    return {'message': 'Оплата произведена. У вас есть 5 минут, чтобы выехать с парковки. Удачного пути!'}

@app.post("/exit")
def exit_the_parking(data: CarExitSchema):
    exit_at = data.exit_at.replace(tzinfo=None)
    with Session(engine) as session:
        stmt = select(CarModel.payment_at).where(CarModel.car_number == data.car_number)
        payment_at = session.scalar(stmt)
    if not payment_at:
        with Session(engine) as session:
            stmt = select(CarModel.entry_at).where(CarModel.car_number == data.car_number)
            entry_at = session.scalar(stmt).replace(tzinfo=None)
        hours = (exit_at - entry_at).total_seconds() // 3600
        if hours > 1:
            if hours >= 2:
                price = hours * 150
            else:
                price = 100

            return {'message': f'Пожалуйста, оплатите {price} рублей за парковку.'}
        else:
            return {'message': 'Счастливого пути!'}
    minutes = (exit_at - payment_at).total_seconds() // 60
    if minutes > 5:
        return {'message': 'Вы не уложились в 5 минут, чтобы выехать.'}

    stmt = delete(CarModel).where(CarModel.car_number == data.car_number)
    session.execute(stmt)
    session.commit()

    return {'message': 'Счастливого пути!'}