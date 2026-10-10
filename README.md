# Geospatial File Measurement API

A production-oriented FastAPI service for uploading geospatial files, normalizing them with GeoPandas, storing the normalized dataset as GeoParquet, calculating CRS-aware feature measurements, and visualizing features in a browser.

## Architecture

```text
HTTP
  |
  v
API Routes
  |
  v
Controllers
  |
  v
Services
  |----------------------|
  v                      v
Repositories       Geospatial modules
  |                      |
  v                      +-- file IO
SQLite                    +-- CRS
                          +-- measurements
  |
  +----------------------+
                         |
                    GeoParquet
```

Routes are intentionally thin. Controllers coordinate HTTP concerns, services contain application logic, repositories handle persistence, and `app/geospatial` owns GeoPandas/CRS/measurement behavior.

## Project Structure

```text
app/
├── api/routes/
│   ├── files.py
│   ├── measurements.py
│   └── ui.py
├── controllers/
├── core/
├── geospatial/
│   ├── crs.py
│   ├── io.py
│   └── measurements.py
├── models/
├── repositories/
├── schemas/
├── services/
├── static/
├── templates/
└── main.py
tests/
.github/workflows/ci.yml
Dockerfile
docker-compose.yml
```

## Supported Input

`POST /api/files/` accepts:

- `.kml`
- `.zip` containing exactly one `.shp`

The original format is only an ingestion format. The dataset is normalized into a GeoDataFrame and persisted as GeoParquet for downstream processing.

## CRS and Measurement Strategy

The key rule is:

> Never calculate physical area or length directly from latitude/longitude degrees.

The application uses a representative-point-based CRS selection strategy:

```text
Input GeoDataFrame
       |
       v
Validate CRS
       |
       v
Transform to EPSG:4326
       |
       v
union_all().representative_point()
       |
       v
Representative geographic location
       |
       v
GeoPandas estimate_utm_crs()
       |
       v
Selected UTM CRS
       |
       v
Transform the complete GeoDataFrame
       |
       v
Calculate area / length
```

`representative_point()` is used to obtain a representative location for
the dataset. It is not used as the geometry for measurement.

GeoPandas then estimates the UTM CRS from that representative geographic
location. The complete feature geometry is transformed into that CRS
before calculating measurements.

For example, a regional dataset around Bengaluru is estimated to use
UTM zone 43N, EPSG:32643.

This approach is appropriate for regional datasets. A dataset spanning
multiple UTM zones can require a more suitable regional projection or
geodesic calculations with `pyproj.Geod`. That limitation is explicitly
documented rather than assuming one UTM CRS is universally accurate.


## Visualization

Visualization uses a different CRS from measurement.

Leaflet/browser maps consume longitude/latitude coordinates, so the GeoJSON endpoint converts the stored geometry to EPSG:4326 before serialization:

```text
GeoParquet
    |
    v
GeoDataFrame
    |
    v
EPSG:4326
    |
    v
GeoJSON
    |
    v
Leaflet
```

Therefore, the UTM representation is used for measurement while WGS84 is used directly for map visualization.

## API

### Upload

```http
POST /api/files/
```

Multipart field: `file`

### File information

```http
GET /api/files/{id}
```

### Features

```http
GET /api/files/{id}/features
```

### GeoJSON

```http
GET /api/files/{id}/geojson
```

### Measurements

```http
GET /api/files/{id}/measurements
```

### Health

```http
GET /health
```

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/` for the UI and `http://localhost:8000/docs` for Swagger.

## Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest
```

## Design Decisions

### FastAPI

FastAPI provides typed contracts, dependency injection, automatic OpenAPI documentation, and a lightweight Python API layer.

### GeoPandas + Pyogrio

GeoPandas provides the geospatial dataframe abstraction, while Pyogrio provides efficient GDAL-backed vector I/O.

### GeoParquet

GeoParquet is the canonical internal representation. Downstream processing is therefore independent of whether the source was KML or Shapefile.

### SQLite

SQLite stores file metadata for this assessment. A production multi-instance deployment would use PostgreSQL/PostGIS.

### Jinja2 + Leaflet

A small server-rendered UI demonstrates the API and feature visualization without requiring a separate frontend application.

## Production Improvements

- asynchronous/background processing for large files
- object storage for originals and processed data
- PostgreSQL/PostGIS metadata and spatial queries
- authentication and authorization
- structured logging, metrics and tracing
- resource/time limits around GDAL processing
- retention and cleanup policies
- geodesic or region-specific measurement strategies for very large datasets
- stronger content validation for untrusted uploads

## Learning and Future Scope

The project demonstrates API design, geospatial ingestion, CRS handling, measurement, persistence, and browser visualization in a modular Python service.
