from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    feature_count: int
    crs: str
    geometry_types: list[str]
    status: str
    created_at: datetime


class FeatureResponse(BaseModel):
    feature_id: str
    geometry_type: str
    properties: dict
