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
    assert len(results) == 2
    assert "[font-fingerprinting]" in results[0]
    assert "[dimension-fingerprinting]" in results[1]

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

def test_poc_chrome():
    css = """
    @container calccontainer (width: 0px) {
        #calcUbuntu {
            color: orangered;
        }
        #calcWindows {
            display: none;
        }
      }
      @container calccontainer (width: 1.84375px) {
        #calcUbuntu {
            display: none;
        }
        #calcWindows {
            color: blue;
        }
      }
    """
    results = container_detector(css)
    assert len(results) == 2

def test_office_detection():
    css = """
    #testcontainer {
        container-type: inline-size;
        font-family: 'Gill Sans MT', 'Gill Sans';
        font-style: normal;
        font-weight: 100;
        font-size: 11px;
        width: 1cap;
    }
    @container (max-width: 7.5px) {
        p {
            color: green;
        }
        #no {
            display: none;
        }
        #yes {
            display: block;
        }
    }
    """
    results = container_detector(css)
    assert len(results) == 2
    assert any("[font-fingerprinting]" in r for r in results)
    assert any("[dimension-fingerprinting]" in r for r in results)

def test_poc_firefox():
    css = """
    .wrapper {
        width: fit-content;
      }
      #containerCalc {
        container: calccontainer / inline-size;
      }
      #targetCalc {
        width: calc(
          1px *
            (
               (  e  * 0.06314882636070251 - 0.06699182000011206 /  ( 
              327510.10546596383 * 101099.74005273856 )  )  + 
              0.9363944577053189 /  sin(  sin( 86911.80023335948 *  tan( 
              122224.59393033749 )  /  tan( 250486.18265094055 )  +  ( 
              169617.27745474092 )  /  pi  * 19.00493122072233 - 
              0.22360279853455722 )  / 50590.01594434995 +  tan(  ( 
              110958.53977223029 )  + 109345.15143883083 * 99223.79864865377 
              + 0.05425928323529661 )  / 94812.65262083427 *  pi  )  - 
              0.8964629967231303 * -341499.34226304095
            )
        );
      }
      @container calccontainer (width: 293874.6875px) {
        #calcUbuntu {
          color: orangered;
        }
        #calcWindows {
          display: none;
        }
      }
      @container calccontainer (width: 293694.0625px) {
        #calcUbuntu {
          display: none;
        }
        #calcWindows {
          color: blue;
        }
      }
    """
    results = container_detector(css)
    assert len(results) == 2
    assert any("[dimension-fingerprinting]" in r for r in results)