from ai_codegen_pro.core.multi_file_codegen import parse_multi_file_response

def test_multi_file_parse_and_render():
    raw = '''
    [
        {"filename": "mod1.py", "template": "python_module.j2", "context": {"name": "foo", "body": "print(1)"}},
        {"filename": "svc.py", "template": "service.j2", "context": {"service_name": "Bar", "logic": "return 42"}}
    ]
    '''
    out = parse_multi_file_response(raw)
    assert "mod1.py" in out and "svc.py" in out
    assert "def foo()" in out["mod1.py"]
    assert "class BarService" in out["svc.py"]
