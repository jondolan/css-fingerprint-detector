from detectors.calc_detector import detector as complex_calc_detector

def test_detect_simple_calc_with_sin():
    css = """
    div { width: calc(sin(1deg) * 100vw); }
    """
    results = complex_calc_detector(css)
    assert len(results) == 1
    assert "calc(sin(1deg) * 100vw)" in results[0]

def test_detect_nested_calc():
    css = """
    div { width: calc(100px + calc(50% - 20px)); }
    """
    results = complex_calc_detector(css)
    assert len(results) == 1
    assert "calc(100px + calc(50% - 20px))" in results[0]

def test_detect_inverse_trig():
    css = """
    div { width: calc(asin(0.5) * 100px); }
    """
    results = complex_calc_detector(css)
    assert len(results) == 1
    assert "calc(asin(0.5) * 100px)" in results[0]

def test_detect_exponential():
    css = """
    div { width: calc(exp(2) * 50px); }
    """
    results = complex_calc_detector(css)
    assert len(results) == 1
    assert "calc(exp(2) * 50px)" in results[0]

# def test_detect_multiple_operations():
#     css = """
#     div { width: calc(100px + 50px * 2 - 25px / 5); }
#     """
#     results = complex_calc_detector(css)
#     assert len(results) == 1
#     assert "calc(100px + 50px * 2 - 25px / 5)" in results[0]

def test_detect_extreme_values():
    css = """
    div { width: calc(0.00001px * 100); }
    """
    results = complex_calc_detector(css)
    assert len(results) == 1
    assert "calc(0.00001px * 100)" in results[0]

def test_no_complex_calc_detected():
    css = """
    div { width: 100vw; }
    div { margin: calc(100px + 50px); }
    div { width: calc(100% + 8px); }
    div { height: calc(100% - 560px); }
    """
    results = complex_calc_detector(css)
    assert len(results) == 0
