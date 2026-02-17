from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ManualAsset, User
from .auth import get_current_user
from pydantic import BaseModel
from typing import Optional, Dict

router = APIRouter(prefix="/assets", tags=["assets"])

class AssetCreate(BaseModel):
    category: str
    name: str
    institution: Optional[str] = None
    value: float
    currency: str
    details: Optional[Dict] = None

@router.post("/")
def create_asset(asset: AssetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_asset = ManualAsset(
        user_id=current_user.id,
        category=asset.category,
        name=asset.name,
        institution=asset.institution,
        value=asset.value,
        currency=asset.currency,
        details=asset.details
    )
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    return new_asset

@router.get("/")
def list_assets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(ManualAsset).filter(ManualAsset.user_id == current_user.id).all()
