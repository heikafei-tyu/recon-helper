from recon.readers.type_inference import infer


def test_infer_common_types():
    assert infer([]) == "empty"
    assert infer(["1", "2"]) == "integer"
    assert infer(["1.5", "2.0"]) == "number"
    assert infer(["true", "FALSE"]) == "boolean"
    assert infer(["2026-10-02", "2026-10-03"]) == "date"
    assert infer(["001", "text"]) == "text"
