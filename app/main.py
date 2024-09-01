from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.user import router as user_router
from .routers.post import router as post_router
from .routers.auth import router as auth_router
from .routers.vote import router as vote_router

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(post_router, prefix='/posts', tags=['Posts'])
app.include_router(user_router, prefix='/users', tags=['Users'])
app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
app.include_router(vote_router, prefix='/vote', tags=['Votes'])


@app.get("/")
async def root():
    return {"Hello", "world"}
