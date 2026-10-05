from recon.readers.type_inference import infer


def test_infer_common_types():
    assert infer([]) == "empty"
    assert infer(["1", "2"]) == "integer"
    assert infer(["1.5", "2.0"]) == "number"
    assert infer(["true", "FALSE"]) == "boolean"
    assert infer(["2026-10-02", "2026-10-03"]) == "date"
    assert infer(["001", "text"]) == "text"


def test_infer_multiple_date_formats():
    assert infer(["2024/1/1", "2024/1/2"]) == "date"
    assert infer(["20240101", "20240102"]) == "date"
    assert infer(["2024-01-01T12:30:00", "2024-01-02T00:00:00"]) == "date"


def test_infer_financial_number_formats():
    assert infer(["1,234.50", "¥2,000.00"]) == "number"
    assert infer(["12.3%", "8.0%"]) == "number"
    assert infer(["(100)", "200"]) == "integer"


def test_infer_rejects_malformed_numeric_mix():
    assert infer(["1,23.4", "N/A"]) == "text"
