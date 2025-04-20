from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user
from app.services.recommendations_service import get_recommendations
from app.routers.movies import MovieResponse

router = APIRouter()

@router.get("/", response_model=List[MovieResponse])
async def get_recommendations_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_recommendations(db, current_user.id) 