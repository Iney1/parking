from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class CarModel(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_number: Mapped[str]
    entry_at: Mapped[datetime]
    payment_at: Mapped[datetime | None]
    exit_at: Mapped[datetime | None]
    is_gone: Mapped[bool | None]