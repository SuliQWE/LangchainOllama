from fastapi import HTTPException, APIRouter, Depends
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from mysite.database.models import UserProfile, RefreshToken
from mysite.database.schema import (
    UserProfileInputSchema, UserProfileUpdateSchema, UserLoginSchema,
    RequestUserSchema, UserProfileOutSchema
)
from sqlalchemy.orm import Session
from mysite.config import (SECRET_KEY, ALGORITHM,ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME)
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from .dependencies import credentials_exception, get_db, get_current_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login/")

auth_router = APIRouter(prefix="/auth", tags=["AuthVerify"])




def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_LIFETIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_LIFETIME))


def get_token_data(user: UserProfile):
    return {'sub': str(user.id), 'username': user.username, 'status': user.status.value}


@auth_router.post('/register/', response_model=dict)
async def register(user: UserProfileInputSchema, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    email_db = db.query(UserProfile).filter(UserProfile.email == user.email).first()
    if user_db or email_db:
        raise HTTPException(detail="Пользователь с таким юзер неймом или почтой уже существует", status_code=400)

    hash_password = get_password_hash(user.password)
    user_data = UserProfile(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        password=hash_password,
        status=user.status.value
    )

    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return {'message': 'Успешная регистрация'}


@auth_router.post('/login/', response_model=dict)
async def login(user: UserLoginSchema, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    if not user_db or not verify_password(user.password, user_db.password):
        raise HTTPException(status_code=400, detail="Неправильные данные")

    token_data = get_token_data(user_db)

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    token_db = RefreshToken(user_id=user_db.id, token=refresh_token)
    db.add(token_db)
    db.commit()

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'Bearer'}


@auth_router.post('/logout/')
async def logout(refresh_token: str, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not stored_token:
        raise HTTPException(status_code=400, detail="Просрочен токен обновления")

    db.delete(stored_token)
    db.commit()

    return {'message': 'Успешный выход'}


@auth_router.post('/refresh/')
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not stored_token:
        raise HTTPException(status_code=400, detail="Просрочен токен обновления")

    user_db = stored_token.token_user
    token_data = get_token_data(user_db)

    access_token = create_access_token(token_data)

    return {'access_token': access_token, 'token_type': 'Bearer'}


@auth_router.get('/me/', response_model=UserProfileOutSchema)
async def my_profile(current_user: UserProfile = Depends(get_current_user)):
    return current_user


@auth_router.put('/me/update/', response_model=UserProfileOutSchema)
async def update_my_profile(user: UserProfileUpdateSchema, db: Session = Depends(get_db),
                             current_user: UserProfile = Depends(get_current_user)):
    for user_key, user_value in user.dict().items():
        setattr(current_user, user_key, user_value)

    db.commit()
    db.refresh(current_user)
    return current_user


@auth_router.delete('/me/delete/', response_model=dict)
async def delete_my_profile(db: Session = Depends(get_db),
                             current_user: UserProfile = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {'message': 'Юзер удален'}


@auth_router.get('/verify/', response_model=RequestUserSchema)
async def verify_access_token(current_user: UserProfile = Depends(get_current_user)):
    return current_user
