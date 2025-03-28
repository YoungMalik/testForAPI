from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta, datetime
from fastapi.responses import RedirectResponse
import logging
import os

from . import models, schemas, auth, cashe
from .database import Base, engine, get_db as original_get_db
from .schemas import LinkCreate, LinkUpdate

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Временное переопределение для тестов с SQLite
if "PYTEST_CURRENT_TEST" in os.environ:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
    test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()


    app.dependency_overrides[original_get_db] = override_get_db


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)


@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(original_get_db)):
    logger.info(f"Received registration request for email: {user.email}")
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(original_get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/links/shorten", response_model=schemas.Link)
def create_short_link(
        link: LinkCreate,
        db: Session = Depends(original_get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    short_code = cashe.get_short_code(link.original_url)
    if not short_code:
        short_code = generate_short_code()
        while db.query(models.Link).filter(models.Link.short_code == short_code).first():
            short_code = generate_short_code()
        cashe.set_short_code(link.original_url, short_code)

    expiry_date = link.expiry_date or (
            datetime.now() + timedelta(days=int(os.getenv("DEFAULT_LINK_EXPIRY_DAYS", 30)))
    )
    db_link = models.Link(
        original_url=link.original_url,
        short_code=short_code,
        expiry_date=expiry_date,
        user_id=current_user.id
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


@app.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(original_get_db)):
    db_link = db.query(models.Link).filter(models.Link.short_code == short_code).first()
    if not db_link or (db_link.expiry_date and db_link.expiry_date < datetime.now()):
        raise HTTPException(status_code=404, detail="Link not found or expired")
    db_link.clicks += 1
    db.commit()
    return RedirectResponse(url=db_link.original_url, status_code=307)


@app.put("/links/{short_code}", response_model=schemas.Link)
def update_link(
        short_code: str,
        link: LinkUpdate,
        db: Session = Depends(original_get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    db_link = db.query(models.Link).filter(models.Link.short_code == short_code).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")
    if db_link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this link")
    if link.original_url:
        db_link.original_url = link.original_url
        cashe.set_short_code(link.original_url, short_code)
    if link.expiry_date:
        db_link.expiry_date = link.expiry_date
    db.commit()
    db.refresh(db_link)
    return db_link


@app.delete("/links/{short_code}")
def delete_link(
        short_code: str,
        db: Session = Depends(original_get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    db_link = db.query(models.Link).filter(models.Link.short_code == short_code).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")
    if db_link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this link")
    db.delete(db_link)
    db.commit()
    cashe.delete_short_code(db_link.original_url)
    return {"detail": "Link deleted"}


@app.get("/links/{short_code}/stats", response_model=schemas.LinkStats)
def get_link_stats(
        short_code: str,
        db: Session = Depends(original_get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    db_link = db.query(models.Link).filter(models.Link.short_code == short_code).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")
    if db_link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view stats")
    return {"original_url": db_link.original_url, "short_code": short_code, "clicks": db_link.clicks}


def generate_short_code(length: int = 6) -> str:
    import string
    import random
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))