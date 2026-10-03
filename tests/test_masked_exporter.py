import pytest

from recon.exporters.masked_exporter import export_masked_csv, mask_rows


def test_masking(tmp_path):
    rows = [{"name": "张三", "phone": "13812345678", "amount": "12.6"}]
    masked = mask_rows(rows, {"name": "name", "phone": "phone", "amount": "amount"})[0]
    assert masked == {"name": "张*", "phone": "138****5678", "amount": "13"}
    assert export_masked_csv(rows, {"name": "name"}, tmp_path / "x.csv")["rows"] == 1
@pytest.mark.parametrize("rule", ["bad", "", None])
def test_mask_invalid(rule):
    with pytest.raises(ValueError):
        mask_rows([{"x": 1}], {"x": rule})
