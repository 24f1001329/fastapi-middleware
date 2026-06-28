from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uuid
from collections import defaultdict

app = FastAPI()

EMAIL = "24f1001329@ds.study.iitm.ac.in"
BUCKET_SIZE = 10

ALLOWED_ORIGINS = [
    "https://exam.sanand.workers.dev",
    "https://tds.sanand.workers.dev",
    "https://sanand.workers.dev",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "null",
]

rate_store = defaultdict(int)

@app.middleware("http")
async def middleware_stack(request: Request, call_next):

    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    origin = request.headers.get("origin", "")
    allow_origin = origin if origin in ALLOWED_ORIGINS else ""

    if request.method == "OPTIONS":
        if allow_origin:
            headers = {
                "Access-Control-Allow-Origin": allow_origin,
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "X-Request-ID, X-Client-Id, Content-Type",
                "Access-Control-Expose-Headers": "X-Request-ID",
            }
            return Response(status_code=204, headers=headers)
        return Response(status_code=403)

    client_id = request.headers.get("X-Client-Id", "default")
    rate_store[client_id] += 1
    if rate_store[client_id] > BUCKET_SIZE:
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    if allow_origin:
        response.headers["Access-Control-Allow-Origin"] = allow_origin
        response.headers["Access-Control-Expose-Headers"] = "X-Request-ID"

    return response

@app.get("/ping")
async def ping(request: Request):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    return JSONResponse(
        content={"email": EMAIL, "request_id": request_id},
        headers={"X-Request-ID": request_id}
    )