# CSS Fingerprinting Detector

## Quickstart

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Scan a list of web URLs
python3 main.py --log-level WARN --results-dir ./results_top5 example/top5.txt

# Scan a list of local HTML files
python3 main.py --log-level WARN --results-dir ./results_cascading_spy_sheets example/cascading_spy_sheets.txt
```

The tool supports both web URLs (http://, https://) and local HTML files (list of file names relative to the root of this project.)

## Tests

A comprehensive test suite has been built to validate each detector can successfully detect the examples discussed in the original paper.

```python
python3 -m pytest
```

## Analysis

The tool includes basic tools for analyzing the results.

```python
python3 results/analyze_calc.py results_top5/results_top5.json
python3 results/analyze_dynamic.py results_top5/results_top5.json
```

## Discussion

Sites in the wild may not return many detections. This can be either because:

1) these methods are not widely adopted, either because they are novel or other techniques are sufficient (especially for websites, see [fingerprintjs](https://github.com/fingerprintjs/fingerprintjs), [thumbmarkjs](https://github.com/thumbmarkjs/thumbmarkjs), [creepjs](https://github.com/abrahamjuliot/creepjs))
2) there are other methods that do not match the heuristics used here

The detectors implemented in this project attempt to make general case detections, but are scoped to the specific attacks discussed in the source paper. This means "width > 7.5px" does not need to be **exactly** matched, but rather fact it is a container width query.

## Extending this project

Detectors are designed to be easily extendable. For instance, more at-rule detectors can be added by:

1) Using `./detectors/import_detector.py` or similar as a starting point
2) Adding a new test to `./tests`
3) Adding the detector to `./scorer/css_at_rules.py`


If a new category of detector is required, the steps are similar except duplicate all of the above and additionally add the new category to `main.py`.

## Feature list

### **CSS Fingerprinting Techniques**

- **CSS At-Rules** ✅ (`./scorer/css_at_rules.py`)
  - **@container** ✅ (`./detectors/container_detector.py`)
    - Detects container queries that could be used for fingerprinting
    - Identifies font fingerprinting via font-relative units (`ch`, `ex`, `cap`, `ic`)
    - Detects viewport fingerprinting using viewport-relative units (`vw`, `vh`, `vmin`, `vmax`)
    - Identifies element dimension measurements with precise values
    - Detects text measurement via `inline-size` container type
  - **@supports** ✅ (`./detectors/supports_detector.py`)
    - Detects feature support queries that can identify browser versions
    - Captures browser-specific feature implementations
  - **@import** ✅ (`./detectors/import_detector.py`)
    - Identifies external stylesheet imports
    - Can be used to bypass CSS sanitization in email clients
  - **@page** ✅ (`./detectors/page_detector.py`)
    - Detects print-specific styles that can identify print actions
    - Identifies margin manipulations in print layouts

- **CSS Functions** ✅ (`./scorer/css_functions.py`)
  - **calc()** ✅ (`./detectors/calc_detector.py`)
    - Detects complex mathematical expressions that vary by browser
    - Identifies nested `calc()` expressions
    - Detects use of trigonometric functions
    - Identifies extreme numerical values that may expose implementation differences
  - **env()** ✅ (`./detectors/env_detector.py`)
    - Detects usage of environment variables for device fingerprinting
    - Identifies safe-area insets (notches, rounded corners)
    - Detects keyboard inset queries
    - Identifies titlebar area queries
    - Detects viewport segments (foldable devices)
  - **image-set()** ✅ (`./detectors/image_set_detector.py`)
    - Detects resolution-dependent image loading
    - Identifies device pixel ratio queries
    - Detects DPI/DPCM-based image selection

- **Font Detection** ✅ (`./detectors/font_fallback_detector.py`)
  - Analyzes font fallback chains for fingerprinting patterns
  - Detects system font ordering
  - Identifies custom fonts with specific fallbacks
  - Detects unusual generic family placements
  - Identifies long fallback chains

- **Exfiltration Channels** ✅ (`./detectors/exfil_detector.py`)
  - Detects conditional resource loading via CSS
  - Identifies URL patterns in various CSS contexts
  - Analyzes `image-set()` and `url()` function usage
  - Detects potential data exfiltration through CSS properties
