import json
import sys
from operator import itemgetter

def analyze_dynamic_stylesheets(results_file):
    # Read the results file
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Create list to store website stats
    website_stats = []
    
    # Process each website's results
    for site in results:
        url = site['url']
        chrome_count = site['chrome']['loading_analysis']['dynamic_stylesheets']
        firefox_count = site['firefox']['loading_analysis']['dynamic_stylesheets']
        
        # Take the maximum count between browsers
        max_count = max(chrome_count, firefox_count)
        
        website_stats.append({
            'website': url,
            'dynamic_count': max_count,
            'chrome_count': chrome_count,
            'firefox_count': firefox_count
        })
    
    # Sort websites by dynamic stylesheet count in descending order
    sorted_stats = sorted(website_stats, key=itemgetter('dynamic_count'), reverse=True)
    
    # Print results
    print("\nWebsites ranked by number of dynamic stylesheets:")
    print("=" * 70)
    print(f"{'Rank':<6}{'Website':<40}{'Max':<8}{'Chrome':<8}{'Firefox':<8}")
    print("-" * 70)
    for i, stat in enumerate(sorted_stats, 1):
        print(f"{i:<6}{stat['website']:<40}{stat['dynamic_count']:<8}{stat['chrome_count']:<8}{stat['firefox_count']:<8}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_dynamic.py <results_file>")
        sys.exit(1)
    analyze_dynamic_stylesheets(sys.argv[1])
