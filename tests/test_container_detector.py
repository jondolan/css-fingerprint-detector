from detectors.container_detector import detector as container_detector

def test_detect_font_fingerprinting():
    css = """
    #container {
        container-type: inline-size;
        width: 1ch;
    }
    @container (width > 7.5px) {
        div { background: red; }
    }
    """
    results = container_detector(css)
    assert len(results) == 1
    assert "[font-fingerprinting]" in results[0]

def test_detect_viewport_fingerprinting():
    css = """
    #container {
        container-type: inline-size;
        width: 1vw;
    }
    @container (width > 400px) {
        div { background: blue; }
    }
    """
    results = container_detector(css)
    assert len(results) == 1
    assert "[viewport-fingerprinting]" in results[0]

def test_detect_dimension_fingerprinting():
    css = """
    #container {
        container-type: inline-size;
    }
    @container (width > 123.45px) {
        div { background: green; }
    }
    """
    results = container_detector(css)
    assert len(results) == 1
    assert "[dimension-fingerprinting]" in results[0]

def test_detect_text_measurement():
    css = """
    #container {
        container-type: inline-size;
    }
    @container (width > 100px) {
        div { background: yellow; }
    }
    """
    results = container_detector(css)
    assert len(results) == 1
    assert "[text-measurement]" in results[0]

def test_no_fingerprinting_pattern():
    css = """
    #container {
        container-type: size;
    }
    @container (width > 500px) {
        div { background: red; }
    }
    """
    results = container_detector(css)
    assert len(results) == 0

def test_no_container_queries():
    css = """
    body { margin: 0; }
    p { font-size: 14px; }
    """
    results = container_detector(css)
    assert len(results) == 0
