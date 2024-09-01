from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime

from pydantic.types import conint


class PostBase(BaseModel):
    title: str
    content: str
    # Optionalでも規定値を定める
    published: Optional[bool] = True
    # orm_mode=Trueはv2では非推奨、strictで厳密な型チェックを行える。暗黙的な型変換を防ぐ, ConfigDictがv2から推奨
    model_config = ConfigDict(from_attributes=True, strict=True)


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int

    model_config = ConfigDict(from_attributes=True, strict=True)


class PostResponse(BaseModel):
    Post: Post
    votes: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    phone_number: str
    model_config = ConfigDict(from_attributes=True, strict=True)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    model_config = ConfigDict(from_attributes=True, strict=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


class Vote(BaseModel):
    post_id: int
    # Note: direction has below meaning.
    # 1: wanna add vote
    # 0: wanna delete vote
    dir: conint(le=1)
    model_config = ConfigDict(from_attributes=True, strict=True)
