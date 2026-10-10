from uuid import UUID

from pydantic import BaseModel, Field


class Measurement(BaseModel):
    feature_id: str
    geometry_type: str
    area: float | None = Field(default=None, description="Area in square metres")
    area_unit: str | None = None
    length: float | None = Field(default=None, description="Length in metres")
    length_unit: str | None = None


class MeasurementResponse(BaseModel):
    file_id: UUID
    measurements: list[Measurement]
