import geopandas as gpd

from app.geospatial.crs import project_for_measurement


def calculate_measurements(gdf: gpd.GeoDataFrame) -> list[dict]:
    projected = project_for_measurement(gdf)
    results: list[dict] = []

    for index, geometry in projected.geometry.items():
        geometry_type = geometry.geom_type if geometry is not None else "Unknown"
        result = {
            "feature_id": str(index),
            "geometry_type": geometry_type,
            "area": None,
            "area_unit": None,
            "length": None,
            "length_unit": None,
        }

        if geometry is None or geometry.is_empty:
            results.append(result)
            continue

        if geometry_type in {"Polygon", "MultiPolygon"}:
            result["area"] = float(geometry.area)
            result["area_unit"] = "m2"
        elif geometry_type in {"LineString", "MultiLineString"}:
            result["length"] = float(geometry.length)
            result["length_unit"] = "m"

        results.append(result)

    return results
