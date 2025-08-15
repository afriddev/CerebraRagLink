from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request
from fastapi.responses import JSONResponse


class CustomMidlleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            response = await call_next(request)
            if response.status_code == 404:
                return JSONResponse(
                    status_code=404,
                    content={"data": "INVALID_URL"},
                )
            return response
        except Exception as e:
            print(e)
            return JSONResponse(
                status_code=500,
                content={"data": "SERVER_ERROR"},
            )
