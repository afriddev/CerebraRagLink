import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from middleware import CustomMidlleware
from controllers import QaRagControllerRouter


server = FastAPI()


server.add_middleware(
    CORSMiddleware,
    allow_origins=["* "],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@server.exception_handler(RequestValidationError)
async def validation_exception_handler():
    return JSONResponse(
        status_code=400,
        content={
            "data": "BAD_REQUEST",
        },
    )


server.add_middleware(CustomMidlleware)
server.include_router(QaRagControllerRouter, prefix="/api/v1/qa")

if __name__ == "__main__":
    uvicorn.run("main:server", host="127.0.0.1", port=8000, reload=False)
