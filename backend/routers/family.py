from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, family_sharing_table
from .auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/family", tags=["family"])

class ShareInvite(BaseModel):
    recipient_email: str
    can_view_networth: bool = True
    can_view_holdings: bool = False

@router.post("/invite")
def invite_member(invite: ShareInvite, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recipient = db.query(User).filter(User.email == invite.recipient_email).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient user not found. They must register first.")
    
    if recipient.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot share with yourself.")
        
    # Create sharing record
    from sqlalchemy import insert
    stmt = insert(family_sharing_table).values(
        sharer_id=current_user.id,
        recipient_id=recipient.id,
        can_view_networth=invite.can_view_networth,
        can_view_holdings=invite.can_view_holdings
    )
    db.execute(stmt)
    db.commit()
    
    return {"message": f"Successfully shared with {invite.recipient_email}"}

@router.get("/shared-with-me")
def get_shared_access(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Logic to fetch users who shared their data with the current user
    # This is a bit simplified for now
    return {"message": "Fetch logic TBD"}
