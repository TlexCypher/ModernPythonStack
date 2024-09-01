from fastapi import Depends, HTTPException, Response, status, APIRouter
from typing import List, Optional

from .. import schemas, models, database, oauth2
from sqlalchemy.orm import Session
from sqlalchemy import func

router = APIRouter()


# memo
#     sqlalchemy -> pydantic: from_orm(sqlalchemy)
#     pydantic -> sqlalchemy: pydantic.model_dump()


@router.post("/", response_model=schemas.Post)
async def create_posts(post: schemas.PostCreate, db: Session = Depends(database.get_db),
                       current_user: schemas.UserResponse = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/", response_model=List[schemas.PostResponse])
async def get_posts(db: Session = Depends(database.get_db),
                    current_user: schemas.UserResponse = Depends(oauth2.get_current_user),
                    limit: int = 10, skip: int = 0, search: Optional[str] = ""):

    results = (db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)
               .filter(models.Post.title.contains(search)).limit(limit).offset(skip).all())

    return results


@router.get("/{id}", response_model=schemas.PostResponse)
async def get_post(id: int, db: Session = Depends(database.get_db),
                   current_user: schemas.UserResponse = Depends(oauth2.get_current_user)):

    post = (db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)
            .filter(models.Post.id == id).first())

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} was not found.")

    if post.Post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't see other person's posts.")

    return post


@router.delete("/{id}")
async def delete_post(id: int, db: Session = Depends(database.get_db),
                      current_user: schemas.UserResponse = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(id == models.Post.id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} was not found.")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't delete other person's post.")

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
async def update_post(id: int, post: schemas.PostUpdate, db: Session = Depends(database.get_db),
                      current_user: schemas.UserResponse = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(id == models.Post.id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} was not found.")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't update other person's post.")

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()
