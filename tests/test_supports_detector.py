from detectors.supports_detector import detector as supports_detector

def test_detect_supports_rule():
    css = """
    @supports (display: grid) {
      div { display: grid; }
    }
    """
    results = supports_detector(css)
    assert len(results) == 1
    assert "@supports (display: grid)" in results[0]

def test_detect_multiple_supports():
    css = """
    @supports (display: flex) {
      div { display: flex; }
    }
    @supports (display: grid) {
      div { display: grid; }
    }
    """
    results = supports_detector(css)
    assert len(results) == 2
    assert "@supports (display: flex)" in results[0]
    assert "@supports (display: grid)" in results[1]

def test_no_supports_detected():
    css = """
    p { margin: 1em; }
    """
    results = supports_detector(css)
    assert len(results) == 0
