from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from passlib.context import CryptContext
from database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
http_bearer = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()