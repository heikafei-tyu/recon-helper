from recon.anomalies import detect_iqr


def test_anomaly():
    assert detect_iqr([{"x": x} for x in [1, 2, 2, 3, 100]], "x")[0]["row"] == 4
