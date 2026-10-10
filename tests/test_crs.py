import geopandas as gpd
from shapely.geometry import Polygon

from app.geospatial.crs import (
    estimate_measurement_crs,
    get_representative_point,
    project_for_measurement,
    to_visualization_crs,
)


def test_representative_point_is_inside_dataset():
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([
                (77.0, 12.0),
                (77.1, 12.0),
                (77.1, 12.1),
                (77.0, 12.1),
            ])
        ],
        crs="EPSG:4326",
    )

    point = get_representative_point(gdf)

    assert point is not None
    assert gdf.to_crs("EPSG:4326").geometry.union_all().contains(point)


def test_estimates_utm_using_representative_point():
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([
                (77.0, 12.0),
                (77.1, 12.0),
                (77.1, 12.1),
                (77.0, 12.1),
            ])
        ],
        crs="EPSG:4326",
    )

    estimated_crs = estimate_measurement_crs(gdf)

    assert estimated_crs.to_epsg() == 32643


def test_projects_to_measurement_crs():
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([
                (77.0, 12.0),
                (77.001, 12.0),
                (77.001, 12.001),
                (77.0, 12.001),
            ])
        ],
        crs="EPSG:4326",
    )

    projected = project_for_measurement(gdf)

    assert projected.crs.to_epsg() == 32643


def test_visualization_is_wgs84():
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([
                (8540000, 1320000),
                (8540100, 1320000),
                (8540100, 1320100),
                (8540000, 1320100),
            ])
        ],
        crs="EPSG:32643",
    )

    visualization = to_visualization_crs(gdf)

    assert visualization.crs.to_epsg() == 4326
