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
    results = complex_calc_detector(css)
    assert len(results) == 0

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
    results = complex_calc_detector(css)
    assert len(results) == 0

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
    results = complex_calc_detector(css)
    assert len(results) == 1