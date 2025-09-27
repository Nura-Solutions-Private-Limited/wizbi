from datetime import timedelta

import structlog
from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import core.log_config
from apis.utils import OAuth2PasswordBearerWithCookie
from core.config import settings
from core.hashing import Hasher
from core.security import create_access_token
from db.session import get_db
from db.views.login import get_group, get_permission, get_user
from schemas.tokens import RefreshToken, Token

logger = structlog.getLogger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/rebiz/v1/login")


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = get_user(username=username, db=db)
    if not user:
        return False
    if not Hasher.verify_password(password, user.password):
        return False
    return user


@router.post("/login", response_model=Token)
def login_for_access_token(response: Response,
                           form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")
    user_permissions = get_permission(user_id=user.id, db=db)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username, "permissions": user_permissions},
                                       expires_delta=access_token_expires)
    response.set_cookie(key="access_token",
                        value=f"Bearer {access_token}")

    return {"access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "permissions": user_permissions}


@router.post("/refresh-token", response_model=Token)
def refresh_token(refreshToken: RefreshToken,
                  db: Session = Depends(get_db)):
    token_user = get_access_from_refresh_token(db,
                                               refresh_token=refreshToken)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    login_token = create_access_token(user=token_user,
                                      expires_delta=access_token_expires)

    return login_token


def get_access_from_refresh_token(db: Session, refresh_token: str):
    # print('in get access token', refresh_token)

    payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    username: str = payload.get("sub")

    return username


def get_current_user_from_token(token: str = Depends(oauth2_scheme),
                                db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",)
    try:
        payload = jwt.decode(token,
                             settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        # permissions: str = payload.get("permissions")
        logger.info("username/email extracted is: -{}".format(username))
        if username is None:
            logger.error("login")
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user
