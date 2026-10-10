from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.measurement import MeasurementResponse
from app.services.measurement_service import MeasurementService


class MeasurementController:
    def __init__(self, db: Session):
        self.service = MeasurementService(db)

    def get_measurements(self, file_id: UUID) -> MeasurementResponse:
        return self.service.calculate(file_id)
