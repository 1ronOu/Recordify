from datetime import timedelta
import schemas
from targefy_app.authenticaton import utility

TOKEN_TYPE_FIELD = 'type'
ACCESS_TOKEN_TYPE = 'access'
REFRESH_TOKEN_TYPE = 'refresh'


def create_jwt(token_type: str,
               token_data: dict,
               expire_minutes: int = 15,
               expire_timedelta: timedelta | None = None,
               ) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return utility.encode_jwt(payload=jwt_payload,
                              expire_minutes=expire_minutes,
                              expire_timedelta=expire_timedelta,
                              )


def create_access_token(user: schemas.User):
    jwt_payload = {
        'sub': user.username,
        'username': user.username,
        'email': user.email,
    }
    return create_jwt(token_type=ACCESS_TOKEN_TYPE,
                      token_data=jwt_payload,
                      expire_minutes=15,
                      )


def create_refresh_token(user: schemas.User):
    jwt_payload = {
        'sub': user.username,
    }
    return create_jwt(token_type=REFRESH_TOKEN_TYPE,
                      token_data=jwt_payload,
                      expire_timedelta=timedelta(43200),
                      )
