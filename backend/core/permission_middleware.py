import time

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

import constants
from core.config import settings
from db.views.role import RoleType

logger = structlog.getLogger(__name__)


class PermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)

        # Perform actions after the request
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        request_path_list = request.url.path.split('/')
        request_path = 'login'
        if len(request_path_list) >= 4:
            request_path = request_path_list[3]
        if not request_path.startswith('login'):
            if request_path.startswith('register'):
                # avoid authorization check in case of user registeration
                pass
            elif request_path.startswith('docs'):
                pass
            elif request_path.startswith('backdoor-register'):
                if constants.WIZBI_ENV.upper() == 'DEV' and constants.BACKDOOR_USER_REGISTER.upper() == 'Y':
                    pass
            else:
                try:
                    # Get bearer token from cookie,
                    # in case token does not exist then get it from authorization header
                    # in case it does not exist in cookie and header then return unauthorized response
                    if request.cookies.get("access_token"):
                        bearer_token = request.cookies.get("access_token").split(' ')[1]
                        logger.info('cookie authentication')
                    elif request.headers.get("Authorization"):
                        bearer_token = request.headers.get("Authorization")
                        if bearer_token.startswith('Bearer '):
                            bearer_token = bearer_token.split(' ')[1]
                        logger.info('header authorization')
                    else:
                        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                            content="Could not validate credentials",)
                    payload = jwt.decode(bearer_token,
                                         settings.SECRET_KEY,
                                         algorithms=[settings.ALGORITHM])
                    permissions = payload.get("permissions")
                except JWTError:
                    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                        content="Could not validate credentials",)
                if not permissions.get('admin') and permissions.get('role') not in [RoleType.ADMIN.name,
                                                                                    RoleType.ALL.name]:
                    if request_path.startswith('pipeline'):
                        if not permissions.get('pipelines'):
                            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                                content="Not authorized to access pipelines.")
                    elif request_path.startswith('connection') or request_path.startswith('db-conn'):
                        if not permissions.get('connections'):
                            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                                content="Not authorized to access connections.")
                    elif request_path.startswith('dashboard'):
                        if not permissions.get('dashboards'):
                            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                                content="Not authorized to access dashboards.")
                    elif request_path.startswith('job'):
                        if not permissions.get('jobs'):
                            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                                content="Not authorized to access jobs.")
                    elif request_path.startswith('audit'):
                        if not permissions.get('audits'):
                            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                                content="Not authorized to access audits.")
                    elif request_path.startswith('report'):
                        if not permissions.get('reports'):
                            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                                content="Not authorized to access reports.")
        # return await call_next(request)
        return response
