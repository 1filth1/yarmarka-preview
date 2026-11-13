from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import AuditLog, User
from ..schemas import LoginIn, RegisterIn
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    username = data.username.strip().lower()
    if db.scalar(select(User).where(User.username == username)):
        raise HTTPException(status_code=409, detail="Логин уже занят")
    user = User(username=username, password_hash=hash_password(data.password),
                full_name=data.full_name.strip(), role="staff", status="pending")
    db.add(user)
    db.flush()
    db.add(AuditLog(actor_id=user.id, action="registration_submitted",
                    entity_type="user", entity_id=user.id))
    db.commit()
    return {"message": "Заявка отправлена администратору на проверку"}

@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    username = data.username.strip().lower()
    user = db.scalar(select(User).where(User.username == username))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    if user.status != "active":
        raise HTTPException(status_code=403, detail="Учётная запись ожидает подтверждения или заблокирована")
    return {"access_token": create_access_token(user.id, user.role), "token_type": "bearer",
            "user": {"id": user.id, "username": user.username, "full_name": user.full_name,
                     "role": user.role, "department": user.department}}
