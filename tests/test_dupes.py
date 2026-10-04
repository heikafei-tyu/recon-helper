from recon.dupes import find_duplicates


def test_duplicates():
    assert find_duplicates([{"id": 1}, {"id": 1}], ["id"])[0]["count"] == 2
