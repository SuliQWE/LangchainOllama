from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from mysite.database.database import SessionLocal
from mysite.database.models import UserProfile
from mysite.config import SECRET_KEY, ALGORITHM

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login/")

credentials_exception = HTTPException(
    status_code=401,
    detail="Access token ошибка",
    headers={"WWW-Authenticate": "Bearer"}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)) -> UserProfile:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception
        user_id = int(subject)

    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()

    if not user_db:
        raise credentials_exception

    return user_db