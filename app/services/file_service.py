import json
import shutil
from pathlib import Path
from uuid import UUID, uuid4

import geopandas as gpd
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import InvalidGeospatialFileError, ResourceNotFoundError
from app.geospatial.io import read_geospatial_file
from app.models.file import FileRecord
from app.repositories.file_repository import FileRepository


class FileService:
    def __init__(self, db: Session):
        self.repository = FileRepository(db)

    def upload(self, upload: UploadFile):
        filename = Path(upload.filename or "").name
        suffix = Path(filename).suffix.lower()

        if not filename or suffix not in settings.ALLOWED_EXTENSIONS:
            raise InvalidGeospatialFileError(
                "Only KML files and ZIP archives containing a Shapefile are supported."
            )

        file_id = uuid4()
        upload_dir = settings.UPLOAD_DIR / str(file_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        original_path = upload_dir / filename

        try:
            self._save_upload(upload, original_path)
            gdf = read_geospatial_file(original_path)
            self._validate_dataset(gdf)

            parquet_path = settings.PROCESSED_DIR / f"{file_id}.parquet"
            gdf.to_parquet(parquet_path, index=False)

            geometry_types = sorted(
                {geometry.geom_type for geometry in gdf.geometry if geometry is not None}
            )
            record = FileRecord(
                id=str(file_id),
                filename=filename,
                stored_path=str(original_path),
                parquet_path=str(parquet_path),
                feature_count=len(gdf),
                crs=gdf.crs.to_string(),
                geometry_types=json.dumps(geometry_types),
                status="COMPLETED",
            )
            self.repository.create(record)
            return self._serialize(record)
        except Exception:
            shutil.rmtree(upload_dir, ignore_errors=True)
            parquet_path = settings.PROCESSED_DIR / f"{file_id}.parquet"
            parquet_path.unlink(missing_ok=True)
            raise

    def get(self, file_id: UUID):
        return self._serialize(self._get_record(file_id))

    def features(self, file_id: UUID):
        gdf = self._load(file_id)
        records = []
        for idx, row in gdf.iterrows():
            properties = {}
            for column, value in row.items():
                if column == gdf.geometry.name:
                    continue
                properties[column] = _json_safe(value)
            records.append({
                "feature_id": str(idx),
                "geometry_type": row.geometry.geom_type if row.geometry else "Unknown",
                "properties": properties,
            })
        return records

    def geojson(self, file_id: UUID):
        return json.loads(self._load(file_id).to_json())

    def load_geodataframe(self, file_id: UUID) -> gpd.GeoDataFrame:
        return self._load(file_id)

    def _load(self, file_id: UUID) -> gpd.GeoDataFrame:
        record = self._get_record(file_id)
        try:
            return gpd.read_parquet(record.parquet_path)
        except Exception as exc:
            raise InvalidGeospatialFileError(
                "The processed GeoParquet file cannot be read."
            ) from exc

    def _get_record(self, file_id: UUID) -> FileRecord:
        record = self.repository.get(str(file_id))
        if record is None:
            raise ResourceNotFoundError(f"File '{file_id}' was not found.")
        return record

    @staticmethod
    def _save_upload(upload: UploadFile, destination: Path) -> None:
        size = 0
        with destination.open("wb") as output:
            while chunk := upload.file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.MAX_UPLOAD_SIZE:
                    raise InvalidGeospatialFileError("The upload exceeds the 100 MB limit.")
                output.write(chunk)

    @staticmethod
    def _validate_dataset(gdf: gpd.GeoDataFrame) -> None:
        if gdf.empty:
            raise InvalidGeospatialFileError("The file contains no features.")
        if len(gdf) > settings.MAX_FEATURES:
            raise InvalidGeospatialFileError(
                f"The dataset exceeds the {settings.MAX_FEATURES:,} feature limit."
            )
        if gdf.geometry.name not in gdf.columns:
            raise InvalidGeospatialFileError("The dataset does not contain a geometry column.")
        if gdf.crs is None:
            raise InvalidGeospatialFileError("The dataset must define a CRS.")

    @staticmethod
    def _serialize(record: FileRecord):
        return {
            "id": record.id,
            "filename": record.filename,
            "feature_count": record.feature_count,
            "crs": record.crs,
            "geometry_types": json.loads(record.geometry_types),
            "status": record.status,
            "created_at": record.created_at,
        }


def _json_safe(value):
    if hasattr(value, "item"):
        value = value.item()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if value != value:  # NaN
        return None
    return value
