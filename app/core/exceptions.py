from http import HTTPStatus


class GeospatialError(Exception):
    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnsupportedFileTypeError(GeospatialError):
    status_code = HTTPStatus.UNSUPPORTED_MEDIA_TYPE


class InvalidGeospatialFileError(GeospatialError):
    status_code = HTTPStatus.BAD_REQUEST


class ResourceNotFoundError(GeospatialError):
    status_code = HTTPStatus.NOT_FOUND
