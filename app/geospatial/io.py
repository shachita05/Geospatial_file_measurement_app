from pathlib import Path
import tempfile
import zipfile

import geopandas as gpd

from app.core.exceptions import InvalidGeospatialFileError


def read_geospatial_file(path: Path) -> gpd.GeoDataFrame:
    if path.suffix.lower() == ".kml":
        return _read_vector(path)
    if path.suffix.lower() == ".zip":
        return _read_shapefile_zip(path)
    raise InvalidGeospatialFileError("Unsupported geospatial file format.")


def _read_shapefile_zip(path: Path) -> gpd.GeoDataFrame:
    with tempfile.TemporaryDirectory(prefix="geo-upload-") as directory:
        extraction_dir = Path(directory)
        try:
            with zipfile.ZipFile(path) as archive:
                if archive.testzip() is not None:
                    raise InvalidGeospatialFileError("The ZIP archive is corrupted.")
                for member in archive.infolist():
                    member_path = Path(member.filename)
                    if member_path.is_absolute() or ".." in member_path.parts:
                        raise InvalidGeospatialFileError("The ZIP contains an unsafe path.")
                archive.extractall(extraction_dir)
        except zipfile.BadZipFile as exc:
            raise InvalidGeospatialFileError("The uploaded ZIP is invalid.") from exc

        shapefiles = list(extraction_dir.rglob("*.shp"))
        if len(shapefiles) != 1:
            raise InvalidGeospatialFileError(
                "The ZIP must contain exactly one .shp file and its supporting files."
            )
        return _read_vector(shapefiles[0])


def _read_vector(path: Path) -> gpd.GeoDataFrame:
    try:
        return gpd.read_file(path, engine="pyogrio")
    except Exception as exc:
        raise InvalidGeospatialFileError(
            f"Unable to read the geospatial file: {exc}"
        ) from exc
