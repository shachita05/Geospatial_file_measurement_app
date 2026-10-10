from pathlib import Path

import pytest

from app.core.exceptions import InvalidGeospatialFileError
from app.geospatial.io import read_geospatial_file


def test_unsupported_extension(tmp_path: Path):
    path = tmp_path / "data.txt"
    path.write_text("not geospatial")
    with pytest.raises(InvalidGeospatialFileError):
        read_geospatial_file(path)
