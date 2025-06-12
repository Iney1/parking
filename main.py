from fastapi import FastAPI
from src.endpoints import router
from src.engine import engine
from src.models import Base

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(router)