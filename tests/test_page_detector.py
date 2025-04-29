from detectors.page_detector import detector as print_detector

def test_detect_basic_page_rule():
    css = """
    @page {
      size: A4;
    }
    """
    results = print_detector(css)
    assert len(results) == 1
    assert "@page [basic]" in results[0]

def test_detect_page_with_margins():
    css = """
    @page {
      margin: 2cm;
      margin-top: 3cm;
    }
    """
    results = print_detector(css)
    assert len(results) == 1
    assert "@page [margins]" in results[0]

def test_detect_page_with_pseudo():
    css = """
    @page :first {
      margin: 2cm;
    }
    """
    results = print_detector(css)
    assert len(results) == 1
    assert "@page :first [margins]" in results[0]

def test_detect_multiple_page_rules():
    css = """
    @page {
      size: A4;
    }
    @page :first {
      margin: 2cm;
    }
    """
    results = print_detector(css)
    assert len(results) == 2
    assert "@page [basic]" in results[0]
    assert "@page :first [margins]" in results[1]

def test_no_page_rules():
    css = """
    body { margin: 0; }
    p { font-size: 14px; }
    """
    results = print_detector(css)
    assert len(results) == 0
