import zipfile

from ai_codegen_pro.core.multi_file_codegen import export_zip, parse_multi_file_response


def test_parse_invalid_json():
    out = parse_multi_file_response("not a json")
    assert out == {}


def test_missing_fields():
    raw = '[{"filename": "f.py"}]'  # Kein template, kein context
    out = parse_multi_file_response(raw)
    assert out == {}


def test_unknown_template():
    raw = '[{"filename": "fail.py", "template": "nope.j2", "context": {"foo": 1}}]'
    out = parse_multi_file_response(raw)
    assert out == {}  # Wird geloggt und übersprungen


def test_export_zip_creates_zip(tmp_path):
    file_dict = {"a.py": "print(1)", "b.py": "print(2)"}
    zippath = tmp_path / "test.zip"
    export_zip(file_dict, zippath)
    assert zippath.exists()
    with zipfile.ZipFile(zippath, "r") as z:
        assert sorted(z.namelist()) == ["a.py", "b.py"]
        assert z.read("a.py") == b"print(1)"


def test_large_file_batch():
    files = [
        {
            "filename": f"f{i}.py",
            "template": "python_module.j2",
            "context": {"name": f"f{i}", "body": f"print({i})"},
        }
        for i in range(20)
    ]
    out = parse_multi_file_response(str(files).replace("'", '"'))  # Quick&Dirty
    assert len(out) == 20
