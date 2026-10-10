import geopandas as gpd
from pyproj import CRS


WGS84 = "EPSG:4326"


def get_representative_point(
    gdf: gpd.GeoDataFrame,
):
    """Return a representative geographic point for the dataset.

    The point is used only for CRS selection. It is not used for
    area or length calculations.
    """
    if gdf.empty:
        raise ValueError("Cannot determine a representative point for an empty dataset.")

    if gdf.crs is None:
        raise ValueError("A CRS is required to determine the measurement CRS.")

    wgs84 = gdf.to_crs(WGS84)
    return wgs84.geometry.union_all().representative_point()


def estimate_measurement_crs(
    gdf: gpd.GeoDataFrame,
) -> CRS:
    """Estimate a suitable UTM CRS using a representative point.

    GeoPandas' ``estimate_utm_crs`` is used as the primary CRS
    estimation strategy. The representative point provides the
    geographic location used for CRS selection.

    This is intended for regional datasets. Datasets spanning
    multiple UTM zones may require a regional projection or
    geodesic measurement strategy instead.
    """
    representative_point = get_representative_point(gdf)

    # Create a one-point WGS84 GeoDataFrame so GeoPandas can estimate
    # the UTM CRS from the representative location.
    representative_gdf = gpd.GeoDataFrame(
        geometry=[representative_point],
        crs=WGS84,
    )

    estimated_crs = representative_gdf.estimate_utm_crs()

    if estimated_crs is None:
        raise ValueError(
            "Unable to estimate a suitable projected CRS "
            "from the representative point."
        )

    return estimated_crs


def project_for_measurement(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Project geometries into the estimated UTM CRS for measurements."""
    if gdf.crs is None:
        raise ValueError("A CRS is required for measurement.")

    if gdf.crs.is_projected:
        return gdf

    measurement_crs = estimate_measurement_crs(gdf)
    return gdf.to_crs(measurement_crs)


def to_visualization_crs(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Return geometries in WGS84 for browser/map visualization."""
    if gdf.crs is None:
        raise ValueError("A CRS is required for visualization.")

    if gdf.crs.to_string() == WGS84:
        return gdf

    return gdf.to_crs(WGS84)
