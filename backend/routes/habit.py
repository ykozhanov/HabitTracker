from fastapi import APIRouter, Depends

from ..database import get_session

router = APIRouter()
