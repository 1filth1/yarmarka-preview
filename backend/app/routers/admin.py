from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import admin_user
from ..models import AuditLog, User
from ..schemas import UserOut

router = APIRouter(prefix="/api/admin", tags=["administration"])

@router.get("/pending-users", response_model=list[UserOut])
def pending_users(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(User).where(User.status == "pending").order_by(User.created_at)))

@router.post("/users/{user_id}/approve", response_model=UserOut)
def approve_user(user_id: int, department: str, admin: User = Depends(admin_user),
                 db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.status != "pending":
        raise HTTPException(status_code=409, detail="Заявка уже обработана")
    if not department.strip():
        raise HTTPException(status_code=422, detail="Укажите отдел")
    user.department = department.strip()
    user.status = "active"
    db.add(AuditLog(actor_id=admin.id, action="user_approved", entity_type="user", entity_id=user.id))
    db.commit()
    db.refresh(user)
    return user

@router.post("/users/{user_id}/reject")
def reject_user(user_id: int, admin: User = Depends(admin_user), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.status = "rejected"
    db.add(AuditLog(actor_id=admin.id, action="user_rejected", entity_type="user", entity_id=user.id))
    db.commit()
    return {"message": "Заявка отклонена"}
