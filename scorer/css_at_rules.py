# From section IV of "Cascading Spy Sheets"

# Section IV-A
from detectors.container_detector import detector as container_detector

# Section IV-B
from detectors.supports_detector import detector as supports_detector
from detectors.import_detector import detector as import_detector
from detectors.page_detector import detector as print_detector

def scorer(css):

    results = {
        "container_rules": {
            "count": 0,
            "matches": []
        },
        "supports_rules": {
            "count": 0,
            "matches": []
        },
        "import_rules": {
            "count": 0,
            "matches": []
        },
        "page_rules": {
            "count": 0,
            "matches": []
        }
    }

    for css_text in css:

        container_matches = container_detector(css_text)
        results["container_rules"]["matches"].extend(container_matches)
        results["container_rules"]["count"] += len(container_matches)

        supports_matches = supports_detector(css_text)
        results["supports_rules"]["matches"].extend(supports_matches)
        results["supports_rules"]["count"] += len(supports_matches)

        import_matches = import_detector(css_text)
        results["import_rules"]["matches"].extend(import_matches)
        results["import_rules"]["count"] += len(import_matches)

        page_matches = print_detector(css_text)
        results["page_rules"]["matches"].extend(page_matches)
        results["page_rules"]["count"] += len(page_matches)

    return results
