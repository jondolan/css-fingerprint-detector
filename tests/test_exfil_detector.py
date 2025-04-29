import pytest
from detectors.exfil_detector import detector

def test_basic_url():
    css = """
    .test {
        background-image: url('test.jpg');
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "url(test.jpg) in background-image" in results[0]

def test_image_set():
    css = """
    .test {
        background-image: image-set(
            "test1.jpg" 1x,
            "test2.jpg" 2x
        );
    }
    """
    results = detector(css)
    assert len(results) == 2
    assert any("image-set(test1.jpg) in background-image" in r for r in results)
    assert any("image-set(test2.jpg) in background-image" in r for r in results)

def test_media_query():
    css = """
    @media (min-width: 800px) {
        .test {
            background: url("wide.jpg");
        }
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "[@media (min-width: 800px)]" in results[0]

def test_container_query():
    css = """
    @container (min-width: 800px) {
        .test {
            background: url("container.jpg");
        }
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "[@container (min-width: 800px)]" in results[0]

def test_supports_rule():
    css = """
    @supports (display: grid) {
        .test {
            background: url("grid.jpg");
        }
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "[@supports (display: grid)]" in results[0]

def test_multiple_urls():
    css = """
    .test {
        background-image: url("bg.jpg");
        border-image: url("border.png");
    }
    """
    results = detector(css)
    assert len(results) == 2
    assert any("url(bg.jpg) in background-image" in r for r in results)
    assert any("url(border.png) in border-image" in r for r in results)

def test_data_url_ignored():
    css = """
    .test {
        background: url("data:image/png;base64,abc123");
        border-image: url("real.png");
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "url(real.png) in border-image" in results[0]

def test_type_declaration():
    css = """
    .test {
        content: image("test.jpg" type("image/jpeg"));
    }
    """
    results = detector(css)
    assert len(results) == 1
    assert "image(test.jpg) in content" in results[0]

def test_resolution_specifiers():
    css = """
    .test {
        background: image-set(
            "test1.jpg" type("image/jpeg") 1x,
            "test2.jpg" type("image/jpeg") 2x
        );
    }
    """
    results = detector(css)
    assert len(results) == 2
    assert any("image-set(test1.jpg) in background" in r for r in results)
    assert any("image-set(test2.jpg) in background" in r for r in results)
