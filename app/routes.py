from fastapi import APIRouter, HTTPException, Depends, status, Form, File, UploadFile
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
import shutil
import os
from pathlib import Path
from app.database import get_database
from app.models import BlogPostResponse
from app.auth import verify_admin

router = APIRouter()

# Helper function to convert MongoDB _id to string
def post_helper(post) -> dict:
    return {
        "id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"],
        "category": post["category"],
        "createdAt": post["createdAt"],
        "image": post["image"],
        "author": post["author"],
        "isPublished": post["isPublished"]
    }

@router.get("/posts", response_model=List[BlogPostResponse])
async def get_posts(db=Depends(get_database)):
    posts = []
    cursor = db.posts.find({"isPublished": True}).sort("createdAt", -1)
    async for post in cursor:
        posts.append(post_helper(post))
    return posts

@router.get("/posts/{id}", response_model=BlogPostResponse)
async def get_post(id: str, db=Depends(get_database)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid post ID")
    
    post = await db.posts.find_one({"_id": ObjectId(id)})
    
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post_helper(post)

@router.post("/posts", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("General"),
    author: str = Form(...),
    isPublished: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db=Depends(get_database), 
    admin: str = Depends(verify_admin)
):
    image_url = "https://via.placeholder.com/800"

    if image:
        # Get the absolute path to the backend directory
        BASE_DIR = Path(__file__).resolve().parent.parent
        UPLOAD_DIR = BASE_DIR / "uploads"
        
        # Ensure the uploads folder exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        file_location = UPLOAD_DIR / image.filename
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Store the relative path. The frontend will prepend the domain.
        image_url = f"/uploads/{image.filename}"

    post_dict = {
        "title": title,
        "content": content,
        "category": category,
        "author": author,
        "isPublished": isPublished,
        "createdAt": datetime.utcnow(),
        "image": {"url": image_url}
    }

    result = await db.posts.insert_one(post_dict)
    new_post = await db.posts.find_one({"_id": result.inserted_id})
    return post_helper(new_post)

@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: str, 
    db=Depends(get_database), 
    admin: str = Depends(verify_admin)
):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid post ID")
        
    delete_result = await db.posts.delete_one({"_id": ObjectId(id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return None