from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app import models, database, schemas
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
) -> models.User:
    try:
        if db.query(models.BlacklistedToken).filter_by(token=token).first():
            raise HTTPException(status_code=401, detail="Token has been revoked")

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = db.query(models.User).get(int(user_id))
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(form: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter_by(email=form.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        email=form.email,
        hashed_password=get_password_hash(form.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("New user registered: %s", form.email)
    return new_user


@router.post("/token", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter_by(email=form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    logger.info("User logged in: %s", user.email)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    if db.query(models.BlacklistedToken).filter_by(token=token).first():
        raise HTTPException(status_code=400, detail="Token already invalidated")
    db.add(models.BlacklistedToken(token=token))
    db.commit()
    return {"msg": "Logged out successfully"}


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user
