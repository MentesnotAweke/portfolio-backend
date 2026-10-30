from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ImageModel(BaseModel):
    url: str

class BlogPostBase(BaseModel):
    title: str
    content: str
    category: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    image: ImageModel
    author: str
    isPublished: bool = True

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostResponse(BlogPostBase):
    # The MongoDB _id is an ObjectId, but we will convert it to a string for the frontend
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }