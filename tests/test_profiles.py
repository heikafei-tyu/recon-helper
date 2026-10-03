import pytest
from recon.cli import main
from recon.profiles import list_profiles, show_profile, use_profile


def test_profile_list_and_show():
    assert {item["id"] for item in list_profiles()} == {"strict", "宽松"}
    assert show_profile("strict")["name"] == "严格模式"


def test_profile_use_writes_json(tmp_path):
    result = use_profile("宽松", tmp_path / "profile.json")
    assert result["profile"] == "宽松"
    assert (tmp_path / "profile.json").exists()


@pytest.mark.parametrize("name", ["missing", "", "strict-mode"])
def test_unknown_profile(name):
    with pytest.raises(ValueError):
        show_profile(name)


def test_profile_cli(capsys, tmp_path):
    assert main(["profile", "list"]) == 0
    assert "严格模式" in capsys.readouterr().out
    assert main(["profile", "use", "strict", "--out", str(tmp_path / "p.json")]) == 0
