from recon.profile import column_profile


def test_profile():
    assert column_profile([{"x": 1}, {"x": 3}])["x"]["mean"] == "2"
