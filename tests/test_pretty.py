from recon.pretty import colorize, format_difference


def test_pretty():
    assert "\033[31m" in colorize("bad", "mismatch")
    assert format_difference({"status": "equal"}, False).startswith("[equal]")
