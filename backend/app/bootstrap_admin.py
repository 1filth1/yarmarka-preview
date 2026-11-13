"""Create the first administrator from environment variables; run inside the API container."""
from sqlalchemy import select
from .database import Base, SessionLocal, engine
from .models import User
from .config import settings
from .security import hash_password

def main():
    if not settings.bootstrap_admin_login or not settings.bootstrap_admin_password:
        raise SystemExit("Set BOOTSTRAP_ADMIN_LOGIN and BOOTSTRAP_ADMIN_PASSWORD first")
    if len(settings.bootstrap_admin_password) < 16:
        raise SystemExit("Admin password must be at least 16 characters")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        login = settings.bootstrap_admin_login.strip().lower()
        if db.scalar(select(User).where(User.username == login)):
            raise SystemExit("This login already exists")
        db.add(User(username=login, password_hash=hash_password(settings.bootstrap_admin_password),
                    full_name="Administrator", role="admin", status="active"))
        db.commit()
    print("Administrator created.")

if __name__ == "__main__":
    main()
