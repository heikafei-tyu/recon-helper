import pytest

from recon.readers import read_table


def test_parquet_reader(tmp_path):
    pyarrow = pytest.importorskip("pyarrow")
    import pyarrow.parquet as parquet
    path = tmp_path / "data.parquet"
    parquet.write_table(pyarrow.table({"id": ["A", "B"], "amount": [1, 2]}), path)
    assert read_table(path).summary()["row_count"] == 2


def test_xls_reader_optional():
    pytest.importorskip("xlrd")
