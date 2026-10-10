from uuid import UUID

from sqlalchemy.orm import Session

from app.geospatial.measurements import calculate_measurements
from app.schemas.measurement import MeasurementResponse
from app.services.file_service import FileService


class MeasurementService:
    def __init__(self, db: Session):
        self.file_service = FileService(db)

    def calculate(self, file_id: UUID) -> MeasurementResponse:
        gdf = self.file_service.load_geodataframe(file_id)
        return {"file_id": file_id, "measurements": calculate_measurements(gdf)}
