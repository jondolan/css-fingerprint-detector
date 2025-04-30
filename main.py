import json
import os
import logging
import argparse

# import all the scorer helper functions
from scorer.css_at_rules    import scorer as css_at_rule_scorer
from scorer.css_functions   import scorer as css_function_scorer

# crawler to get css from a URL
from crawler.crawl_page import crawl_single_page

# import css loading analyzer
from analyzer.css_loading_analyzer import analyze_css_loading

def main(urls, results_dir):
    # ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)
    
    results = []

    # iterate through passed in urls
    for url in urls:
        logging.info(f"Obtaining CSS for {url} with both browsers")
        css_sources = crawl_single_page(url)

        # generate url-safe filename
        if url.startswith('file://'):
            # For file:// URLs, use the base filename
            safe_url = os.path.basename(url.replace('file:///', ''))
        else:
            # For http(s):// URLs, remove protocol and convert slashes
            safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_')

        # process Chrome results
        logging.info(f"Processing Chrome results for {url}")
        chrome_css = css_sources['chrome']
        chrome_at_rule_score = css_at_rule_scorer(chrome_css)
        chrome_function_score = css_function_scorer(chrome_css)
        
        chrome_dag_path = os.path.join(results_dir, f"{safe_url}_chrome_loading.png")
        try:
            chrome_loading_analysis = analyze_css_loading(url, chrome_dag_path, 'chrome')
            logging.info(f"Chrome analysis complete, DAG saved to {chrome_dag_path}")
        except Exception as e:
            logging.error(f"Failed to analyze CSS loading with Chrome for {url}: {str(e)}")
            chrome_loading_analysis = None

        # process Firefox results
        logging.info(f"Processing Firefox results for {url}")
        firefox_css = css_sources['firefox']
        firefox_at_rule_score = css_at_rule_scorer(firefox_css)
        firefox_function_score = css_function_scorer(firefox_css)
        
        firefox_dag_path = os.path.join(results_dir, f"{safe_url}_firefox_loading.png")
        try:
            firefox_loading_analysis = analyze_css_loading(url, firefox_dag_path, 'firefox')
            logging.info(f"Firefox analysis complete, DAG saved to {firefox_dag_path}")
        except Exception as e:
            logging.error(f"Failed to analyze CSS loading with Firefox for {url}: {str(e)}")
            firefox_loading_analysis = None

        # prepare Chrome results
        chrome_result = {
            "css_at_rules_score": chrome_at_rule_score,
            "css_function_score": chrome_function_score,
            "loading_analysis": chrome_loading_analysis,
            "loading_dag_file": os.path.basename(chrome_dag_path) if chrome_loading_analysis else None,
            "css_sources_count": len(chrome_css)
        }

        # prepare Firefox results
        firefox_result = {
            "css_at_rules_score": firefox_at_rule_score,
            "css_function_score": firefox_function_score,
            "loading_analysis": firefox_loading_analysis,
            "loading_dag_file": os.path.basename(firefox_dag_path) if firefox_loading_analysis else None,
            "css_sources_count": len(firefox_css)
        }
        
        # combine results into a single entry per URL
        combined_result = {
            "url": url,
            "chrome": chrome_result,
            "firefox": firefox_result
        }
        results.append(combined_result)

        logging.info(f"Analysis complete for {url}, results saved")

    return results


# enable python logging library
def setup_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

# parse logging level argument
def parse_args():
    parser = argparse.ArgumentParser(description="CSS Fingerprinting Detector")

    # logging level argument
    parser.add_argument(
        "--log-level",
        type=str,
        default="WARNING",
        help="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: WARNING)"
    )

    # text file with URLs argument
    parser.add_argument(
        "url_file",
        nargs="?",
        type=str,
        help="Path to text file containing list of URLs to scan"
    )

    # where to write out results
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results",
        help="Directory for output files (default: results/)"
    )

    return parser.parse_args()

# simple main to parse args, setup logging, and then call the main function!
if __name__ == "__main__":
    # get arguments with argparse
    args = parse_args()

    # configure logging level
    setup_logging(args.log_level)

    # check existence of url file
    if not args.url_file or not os.path.exists(args.url_file):
        logging.error(f"URL file not provided or does not exist.")
        exit()

    # get base name of input file (e.g., "top5" from "example/top5.txt")
    input_base = os.path.splitext(os.path.basename(args.url_file))[0]
    
    # list of websites/files to scan from text file
    with open(args.url_file, 'r') as f:
        urls = []
        for line in f:
            line = line.strip()
            if line:
                # Convert relative file paths to file:// URLs
                if not line.startswith(('http://', 'https://', 'file://')):
                    abs_path = os.path.abspath(line)
                    line = 'file:///' + abs_path.lstrip('/')
                urls.append(line)

        results = main(urls, args.results_dir)
        
        # save json results with name matching input file
        results_json = os.path.join(args.results_dir, f"results_{input_base}.json")
        with open(results_json, 'w') as out_f:
            json.dump(results, out_f, indent=2)
