from recon.init_wizard import run_wizard


def test_init_confirm(tmp_path):
    answers = iter(["left.csv", "right.csv", "id", "amount,qty", "0.01", "y"])
    result = run_wizard(tmp_path / "rules.yaml", lambda _: next(answers), lambda _: None)
    assert result["saved"] and (tmp_path / "rules.yaml").exists()
def test_init_cancel(tmp_path):
    answers = iter(["l", "r", "id", "amount", "0", "n"])
    assert not run_wizard(tmp_path / "x.yaml", lambda _: next(answers), lambda _: None)["saved"]
