<<<<<<< HEAD
import os
from contextlib import asynccontextmanager
from os import path

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from jose import JWTError, jwt

import constants
from apis.base import api_router
from core.app_security_middleware import AppSecMiddleware
from core.config import settings
from core.exception_middleware import ExceptionMiddleware
from core.permission_middleware import PermissionMiddleware
from db.appdb import AppDB
from db.base import Base
from db.session import engine
from db.utils import check_db_connected, check_db_disconnected
from db.views.role import RoleType
from util import configure_logger

log_level = os.getenv("LOG_LEVEL", "INFO")
is_debug = log_level == "DEBUG"
configure_logger(log_level)

logger = structlog.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Upgrade database on start
    app_db = AppDB()
    app_db.upgrade_db_on_start()
    yield


def include_router(app):
    app.include_router(api_router)


origins = {
    "http://localhost",
    "http://localhost:3000",
}


def start_application():
    logger.info("Starting wizbi api server")
    app = FastAPI(title=settings.PROJECT_NAME,
                  version=settings.PROJECT_VERSION,
                  swagger_ui_parameters={"defaultModelsExpandDepth": -1},
                  docs_url='/wizbi/docs',
                  debug=True,
                  lifespan=lifespan)
    app.add_middleware(AppSecMiddleware)
    app.add_middleware(ExceptionMiddleware)
    app.add_middleware(PermissionMiddleware)
    app.add_middleware(CORSMiddleware,
                       allow_origins=origins,
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"],
                       )
    include_router(app)
    add_pagination(app)
    logger.info("Started wizbi api server")
    return app


app = start_application()
=======
from app.api.api_v1.api import api_router
from app.core.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {"message": "Welcome to Wizbi API"}
>>>>>>> f51b7047a2043655136d40320d507721426366cb
