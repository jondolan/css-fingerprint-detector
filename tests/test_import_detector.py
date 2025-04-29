from detectors.import_detector import detector as import_detector

def test_detect_import_rule():
    css = """
    @import url('https://example.com/style.css');
    """
    results = import_detector(css)
    assert len(results) == 1
    assert "https://example.com/style.css" in results[0]

def test_detect_multiple_imports():
    css = """
    @import url('style1.css');
    @import url("style2.css");
    """
    results = import_detector(css)
    assert len(results) == 2
    assert "style1.css" in results[0]
    assert "style2.css" in results[1]

def test_no_import_detected():
    css = """
    body { background-color: white; }
    """
    results = import_detector(css)
    assert len(results) == 0
