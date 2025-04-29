import pytest
from detectors.font_fallback_detector import detector

def test_basic_font_fallback():
    css = """
    .test {
        font-family: Arial, sans-serif;
    }
    """
    results = detector(css)
    assert len(results) == 0  # Basic fallback is normal, shouldn't trigger

def test_system_font_chain():
    css = """
    .test {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui;
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "system-font-chain" in results[0]
    assert "-apple-system" in results[0]

def test_custom_font_with_fallback():
    css = """
    .test {
        font-family: "Custom Font", Arial, sans-serif;
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "custom-with-fallback: Custom Font" in results[0]

def test_generic_family_not_last():
    css = """
    .test {
        font-family: Arial, monospace, "Courier New";
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "generic-family-not-last" in results[0]

def test_long_fallback_chain():
    css = """
    .test {
        font-family: "Custom Font", Arial, "Helvetica Neue", -apple-system, system-ui;
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "long-chain: 5 fonts" in results[0]

def test_media_query_context():
    css = """
    @media (min-width: 800px) {
        .test {
            font-family: Monaco, Consolas, monospace;
        }
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "[@media (min-width: 800px)]" in results[0]

def test_multiple_patterns():
    css = """
    .test {
        font-family: "Custom Font", -apple-system, BlinkMacSystemFont, monospace, Arial;
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "system-font-chain" in results[0]
    assert "custom-with-fallback" in results[0]
    assert "generic-family-not-last" in results[0]
    assert "long-chain" in results[0]

def test_quoted_font_names():
    css = """
    .test {
        font-family: "Font With Spaces", 'Single Quoted Font', sans-serif;
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "Font With Spaces" in results[0]
    assert "Single Quoted Font" in results[0]
