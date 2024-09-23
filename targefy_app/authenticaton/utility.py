import uuid
from datetime import timedelta, datetime, timezone
import jwt
from targefy_app.authenticaton.dependencies import pwd_context
SECRET_KEY = '6d68118356edaa0acaad31719b6c3165b29f537c923a05017f80894a58c64509'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def encode_jwt(
    payload: dict,
    private_key: str = SECRET_KEY,
    algorithm: str = ALGORITHM,
    expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded
