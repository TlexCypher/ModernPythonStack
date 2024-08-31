from fastapi import FastAPI
from .database import engine
from . import models
from sqlalchemy_utils import create_database, database_exists
from .routers.user import router as user_router
from .routers.post import router as post_router
from .routers.auth import router as auth_router

app = FastAPI()

if not database_exists(engine.url):
    create_database(engine.url)

models.Base.metadata.create_all(bind=engine)

app.include_router(post_router, prefix='/posts', tags=['Posts'])
app.include_router(user_router, prefix='/users', tags=['Users'])
app.include_router(auth_router, prefix='/auth', tags=['Authentication'])


@app.get("/")
async def root():
    return {"Hello", "world"}
