from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.controllers.file_controller import FileController
from app.core.database import get_db
from app.schemas.file import FeatureResponse, FileResponse

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)) -> FileResponse:
    return FileController(db).upload(file)


@router.get("/{file_id}", response_model=FileResponse)
def get_file(file_id: UUID, db: Session = Depends(get_db)) -> FileResponse:
    return FileController(db).get(file_id)


@router.get("/{file_id}/features", response_model=list[FeatureResponse])
def get_features(file_id: UUID, db: Session = Depends(get_db)) -> list[FeatureResponse]:
    return FileController(db).features(file_id)


@router.get("/{file_id}/geojson")
def get_geojson(file_id: UUID, db: Session = Depends(get_db)):
    return FileController(db).geojson(file_id)
