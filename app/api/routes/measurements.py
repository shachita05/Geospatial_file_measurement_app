from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.measurement_controller import MeasurementController
from app.core.database import get_db
from app.schemas.measurement import MeasurementResponse

router = APIRouter(prefix="/api/files", tags=["measurements"])


@router.get("/{file_id}/measurements", response_model=MeasurementResponse)
def get_measurements(file_id: UUID, db: Session = Depends(get_db)) -> MeasurementResponse:
    return MeasurementController(db).get_measurements(file_id)
