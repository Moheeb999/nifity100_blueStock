import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers import (
    clusters,
    companies,
    documents,
    health,
    peers,
    portfolio,
    screener,
    sectors,
    valuation,
)
from src.api.schemas.error import ErrorResponse

app = FastAPI(
    title="Nifty100 Analytics API",
    version="1.0.0",
    description="REST API for Nifty100 Analytics Platform",
)

# -------------------- CORS --------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Logging --------------------


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log each incoming HTTP request and its processing time."""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    print(f"{request.method} {request.url.path} " f"- {process_time:.4f} sec")

    return response


# -------------------- Routers --------------------

app.include_router(
    clusters.router,
    prefix="/api/v1",
    tags=["Clusters"],
)

app.include_router(
    companies.router,
    prefix="/api/v1",
    tags=["Companies"],
)

app.include_router(
    screener.router,
    prefix="/api/v1",
    tags=["Screener"],
)

app.include_router(
    sectors.router,
    prefix="/api/v1",
    tags=["Sectors"],
)

app.include_router(
    peers.router,
    prefix="/api/v1",
    tags=["Peers"],
)

app.include_router(
    valuation.router,
    prefix="/api/v1",
    tags=["Valuation"],
)

app.include_router(
    portfolio.router,
    prefix="/api/v1",
    tags=["Portfolio"],
)

app.include_router(
    documents.router,
    prefix="/api/v1",
    tags=["Documents"],
)

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)


@app.get("/", tags=["Default"])
def root():
    """Return the API welcome message."""
    return {"message": "Welcome to Nifty100 Analytics API"}


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    """Return a standardized JSON response for HTTP exceptions."""
    error = ErrorResponse(
        code=exc.status_code,
        message=str(exc.detail),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": error.model_dump()},
    )
