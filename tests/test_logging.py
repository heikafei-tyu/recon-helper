import pytest

from recon.logging_config import configure


def test_logging_levels():
    assert configure("INFO").name == "recon"
    with pytest.raises(ValueError):
        configure("unknown")
