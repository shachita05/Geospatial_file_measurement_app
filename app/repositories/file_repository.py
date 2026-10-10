from sqlalchemy.orm import Session

from app.models.file import FileRecord


class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, record: FileRecord) -> FileRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get(self, file_id: str) -> FileRecord | None:
        return self.db.get(FileRecord, file_id)
