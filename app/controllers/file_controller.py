from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.schemas.file import FeatureResponse, FileResponse
from app.services.file_service import FileService


class FileController:
    def __init__(self, db: Session):
        self.service = FileService(db)

    def upload(self, file: UploadFile) -> FileResponse:
        return self.service.upload(file)

    def get(self, file_id: UUID) -> FileResponse:
        return self.service.get(file_id)

    def features(self, file_id: UUID) -> list[FeatureResponse]:
        return self.service.features(file_id)

    def geojson(self, file_id: UUID):
        return self.service.geojson(file_id)
