from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.files import router as files_router
from app.api.routes.measurements import router as measurements_router
from app.api.routes.ui import router as ui_router
from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import GeospatialError


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.ensure_directories()
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "A production-oriented API for uploading KML or Shapefile ZIP files, "
        "normalizing them to GeoParquet, and calculating feature measurements."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

app.include_router(ui_router)
app.include_router(files_router)
app.include_router(measurements_router)


@app.exception_handler(GeospatialError)
async def geospatial_exception_handler(_: Request, exc: GeospatialError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "version": settings.VERSION}
