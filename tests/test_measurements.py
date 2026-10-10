import geopandas as gpd
from shapely.geometry import LineString, Point, Polygon

from app.geospatial.measurements import calculate_measurements


def test_polygon_area_is_positive_and_in_metres():
    gdf = gpd.GeoDataFrame(
        geometry=[Polygon([(77, 12), (77.001, 12), (77.001, 12.001), (77, 12.001)])],
        crs="EPSG:4326",
    )
    result = calculate_measurements(gdf)
    assert result[0]["area"] > 0
    assert result[0]["area_unit"] == "m2"


def test_linestring_length_is_in_metres():
    gdf = gpd.GeoDataFrame(
        geometry=[LineString([(77, 12), (77.001, 12)])],
        crs="EPSG:4326",
    )
    result = calculate_measurements(gdf)
    assert result[0]["length"] > 0
    assert result[0]["length_unit"] == "m"


def test_point_has_no_measurement():
    gdf = gpd.GeoDataFrame(geometry=[Point(77, 12)], crs="EPSG:4326")
    result = calculate_measurements(gdf)
    assert result[0]["area"] is None
    assert result[0]["length"] is None
