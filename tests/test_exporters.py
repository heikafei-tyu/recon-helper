import json

from recon.exporters import export_csv, export_json, export_markdown, export_pdf


def result():
    return {"differences": [{"status": "mismatch", "column": "amount", "difference": "-1"}]}


def test_csv_json_markdown_exporters(tmp_path):
    csv_result = export_csv(result(), tmp_path / "out.csv")
    assert csv_result["rows"] == 1 and "mismatch" in (tmp_path / "out.csv").read_text(encoding="utf-8-sig")
    export_json(result(), tmp_path / "out.json")
    assert json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))[0]["status"] == "mismatch"
    export_markdown(result(), tmp_path / "out.md")
    assert "| status |" in (tmp_path / "out.md").read_text(encoding="utf-8")


def test_pdf_export_opens(tmp_path):
    export_pdf(result(), tmp_path / "out.pdf")
    assert (tmp_path / "out.pdf").read_bytes().startswith(b"%PDF")
