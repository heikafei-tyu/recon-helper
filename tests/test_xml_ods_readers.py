import zipfile

import pytest

from recon.errors import ReadError
from recon.readers import read_table


def test_xml_reader_normalizes_short_rows(tmp_path):
    path = tmp_path / "table.xml"
    path.write_text("<table><row><cell>id</cell><cell>amount</cell></row><row><cell>A1</cell></row></table>", encoding="utf-8")
    table = read_table(path)
    assert table.columns == ("id", "amount")
    assert table.rows == (("A1", None),)


def test_xml_reader_rejects_invalid_document(tmp_path):
    path = tmp_path / "bad.xml"
    path.write_text("<table>", encoding="utf-8")
    with pytest.raises(ReadError, match="XML"):
        read_table(path)


def test_ods_reader_supports_repeated_cells(tmp_path):
    path = tmp_path / "table.ods"
    content = '''<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><office:body><office:spreadsheet><table:table table:name="Sheet1"><table:table-row><table:table-cell><text:p>id</text:p></table:table-cell><table:table-cell><text:p>amount</text:p></table:table-cell></table:table-row><table:table-row><table:table-cell table:number-columns-repeated="2"><text:p>A1</text:p></table:table-cell></table:table-row></table:table></office:spreadsheet></office:body></office:document-content>'''
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("content.xml", content)
    table = read_table(path)
    assert table.format == "ods"
    assert table.rows == (("A1", "A1"),)


def test_ods_reader_reports_missing_sheet(tmp_path):
    path = tmp_path / "table.ods"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("content.xml", "<root />")
    with pytest.raises(ReadError, match="ODS"):
        read_table(path)
