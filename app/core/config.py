from pathlib import Path


class Settings:
    APP_NAME = "Geospatial File Measurement API"
    VERSION = "1.0.0"
    BASE_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = BASE_DIR / "data"
    UPLOAD_DIR = DATA_DIR / "uploads"
    PROCESSED_DIR = DATA_DIR / "processed"
    TEMPLATES_DIR = BASE_DIR / "app" / "templates"
    STATIC_DIR = BASE_DIR / "app" / "static"
    DATABASE_URL = f"sqlite:///{DATA_DIR / 'app.db'}"
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024
    ALLOWED_EXTENSIONS = {".kml", ".zip"}
    MAX_FEATURES = 250_000

    def ensure_directories(self) -> None:
        for path in (self.DATA_DIR, self.UPLOAD_DIR, self.PROCESSED_DIR):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
