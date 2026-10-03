from recon.schema import validate_schema


def test_schema():
    errors = validate_schema([{"id": "a", "amount": "bad"}, {"id": "b", "amount": ""}], required=["id", "amount"], types={"amount": "number"}, max_null_rate=0)
    assert any("类型" in item for item in errors)
