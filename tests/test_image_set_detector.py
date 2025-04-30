from detectors.image_set_detector import detector as image_set_detector

def test_detect_device_pixel_ratio():
    css = """
    .high-res {
        background-image: image-set(
            "cat.jpg" 1x,
            "cat-2x.jpg" 2x,
            "cat-3x.jpg" 3x
        );
    }
    """
    results = image_set_detector(css)
    assert len(results) == 1
    assert "image-set(1x, 2x, 3x) [device-pixel-ratio]" in results[0]

def test_detect_dpi():
    css = """
    .dpi-aware {
        background-image: image-set(
            "low-res.jpg" 96dpi,
            "high-res.jpg" 192dpi
        );
    }
    """
    results = image_set_detector(css)
    assert len(results) == 1
    assert "image-set(96dpi, 192dpi) [dpi]" in results[0]

def test_detect_dpcm():
    css = """
    .dpcm-aware {
        background-image: image-set(
            "low-res.jpg" 38dpcm,
            "high-res.jpg" 76dpcm
        );
    }
    """
    results = image_set_detector(css)
    assert len(results) == 1
    assert "image-set(38dpcm, 76dpcm) [dpcm]" in results[0]

def test_detect_multiple_image_sets():
    css = """
    .multi-res {
        background-image: image-set("icon.png" 1x, "icon-2x.png" 2x);
        content: image-set("avatar.jpg" 96dpi, "avatar-hd.jpg" 192dpi);
    }
    """
    results = image_set_detector(css)
    assert len(results) == 2
    assert "image-set(1x, 2x) [device-pixel-ratio]" in results[0]
    assert "image-set(96dpi, 192dpi) [dpi]" in results[1]

def test_detect_mixed_units():
    css = """
    .mixed {
        background-image: image-set(
            "photo.jpg" 1x,
            "photo-hd.jpg" 192dpi,
            "photo-print.jpg" 76dpcm
        );
    }
    """
    results = image_set_detector(css)
    assert len(results) == 1
    assert "image-set(1x, 192dpi, 76dpcm) [device-pixel-ratio]" in results[0]

def test_no_image_sets():
    css = """
    .basic {
        background-image: url("image.jpg");
        content: url("icon.png");
    }
    """
    results = image_set_detector(css)
    assert len(results) == 0

def test_image_set_poc():
    css = """
    body {
        background-image: -webkit-image-set(url("/leak/1") 1x, url("/leak/2") 2x, url("/leak/3") 3x);
        background-image: -webkit-image-set(url("/leak/safari") type("image/heif"), url("/leak/notsafari") type("image/jpeg"));
        background-image: -webkit-image-set(url("/leak/96") 96dpi, url("/leak/252") 252dpi);
    }
    """
    results = image_set_detector(css)
    assert len(results) == 3