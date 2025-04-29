from detectors.env_detector import detector as env_detector

def test_detect_safe_area():
    css = """
    .notch-area {
        padding-top: env(safe-area-inset-top);
        padding-right: env(safe-area-inset-right);
    }
    """
    results = env_detector(css)
    assert len(results) == 2
    assert "env(safe-area-inset-top) [safe-area]" in results[0]
    assert "env(safe-area-inset-right) [safe-area]" in results[1]

def test_detect_keyboard():
    css = """
    .input-area {
        margin-bottom: env(keyboard-inset-bottom);
    }
    """
    results = env_detector(css)
    assert len(results) == 1
    assert "env(keyboard-inset-bottom) [keyboard]" in results[0]

def test_detect_titlebar():
    css = """
    .window-content {
        top: env(titlebar-area-height);
        left: env(titlebar-area-x);
    }
    """
    results = env_detector(css)
    assert len(results) == 2
    assert "env(titlebar-area-height) [titlebar]" in results[0]
    assert "env(titlebar-area-x) [titlebar]" in results[1]

def test_detect_custom_env():
    css = """
    .custom {
        --my-var: env(custom-environment-variable);
    }
    """
    results = env_detector(css)
    assert len(results) == 1
    assert "env(custom-environment-variable) [custom]" in results[0]

def test_no_env_functions():
    css = """
    body {
        margin: 0;
        padding: 20px;
    }
    """
    results = env_detector(css)
    assert len(results) == 0

def test_detect_viewport_segments():
    css = """
    .foldable {
        grid-template-columns: env(viewport-segment-width 0 0) env(viewport-segment-width 1 0);
        grid-template-rows: env(viewport-segment-height 0 0);
    }
    """
    results = env_detector(css)
    assert len(results) == 3
    assert "env(viewport-segment-width 0 0) [foldable]" in results[0]
    assert "env(viewport-segment-width 1 0) [foldable]" in results[1]
    assert "env(viewport-segment-height 0 0) [foldable]" in results[2]

def test_detect_safe_area_variations():
    css = """
    .safe-areas {
        padding: env(safe-area-inset-top);
        margin: env(safe-area-inset-bottom);
        left: env(safe-area-inset-left);
        right: env(safe-area-inset-right);
        /* Test with additional values */
        padding-top: env(safe-area-inset-top-extra);
        margin-bottom: env(safe-area-inset-bottom-value);
    }
    """
    results = env_detector(css)
    assert len(results) == 6
    for result in results:
        assert "[safe-area]" in result

def test_detect_multiple_env_in_one_value():
    css = """
    .complex {
        padding: env(safe-area-inset-top) env(viewport-segment-width 0 0);
    }
    """
    results = env_detector(css)
    assert len(results) == 2
    assert "env(safe-area-inset-top) [safe-area]" in results[0]
    assert "env(viewport-segment-width 0 0) [foldable]" in results[1]
