from fastapi import FastAPI

from routers import users, trucks

app = FastAPI()

app.include_router(trucks.router)
