import time

import structlog
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

import constants
from core.app_exceptions import LicenseExpiredError
from core.config import settings
from core.security import check_license
from db.views.role import RoleType

logger = structlog.getLogger(__name__)


class AppSecMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not await check_license():
            raise LicenseExpiredError("License expired, Please contact support.")

        response = await call_next(request)

        # Perform actions after the request
        # process_time = time.time() - start_time
        # response.headers["X-Process-Time"] = str(process_time)
        # print(f"Processed request in {process_time} seconds")

        # TODO: Add security headers to response

        return response
