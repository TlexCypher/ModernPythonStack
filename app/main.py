from fastapi import FastAPI, HTTPException, Depends, Response, status
from .database import engine, get_db
from . import models, schemas
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.orm import Session
from typing import List

app = FastAPI()

if not database_exists(engine.url):
    create_database(engine.url)

models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"Hello", "world"}


@app.post("/create_post", response_model=schemas.PostResponse)
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts", response_model=List[schemas.PostBase])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.get("/posts/{id}", response_model=schemas.PostResponse)
async def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=404, detail=f"post with id:{id} was not found.")

    return post


@app.delete("/posts/{id}")
async def delete_post(id: int, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(id == models.Post.id)
    if post_query.first() is None:
        raise HTTPException(status_code=404, detail=f"post with id:{id} was not found.")

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.PostResponse)
async def update_post(id: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(id == models.Post.id)

    if post_query.first() is None:
        raise HTTPException(status_code=404, detail=f"post with id:{id} was not found.")

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()
