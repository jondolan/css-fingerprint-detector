# From section V of "Cascading Spy Sheets"

# Section V-A
from detectors.calc_detector import detector as calc_detector

# Section V-B
from detectors.env_detector import detector as env_detector

# Section III
from detectors.image_set_detector import detector as image_set_detector

def scorer(css):
    # score css for function-based fingerprinting patterns from section v of the paper
    results = {
        "calc_functions": {
            "count": 0,
            "matches": [],
        },
        "env_functions": {
            "count": 0,
            "matches": [],
        },
        "image_set_functions": {
            "count": 0,
            "matches": [],
        }
    }

    for css_text in css:

        calc_matches = calc_detector(css_text)
        results["calc_functions"]["matches"].extend(calc_matches)
        results["calc_functions"]["count"] += len(calc_matches)


        env_matches = env_detector(css_text)
        results["env_functions"]["matches"].extend(env_matches)
        results["env_functions"]["count"] += len(env_matches)

        image_set_matches = image_set_detector(css_text)
        results["image_set_functions"]["matches"].extend(image_set_matches)
        results["image_set_functions"]["count"] += len(image_set_matches)

    return results
