import traceback

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.app_exceptions import LicenseExpiredError

logger = structlog.getLogger(__name__)


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except LicenseExpiredError as exc:
            logger.error(f"License expired: {exc}")
            return JSONResponse(
                status_code=403,
                content={"detail": exc.message})
        except Exception as exc:
            logger.error(f"An unexpected error occurred: {exc}")
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={"detail": "An unexpected error occurred. Please try again later."})
