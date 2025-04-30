import json
import sys
from operator import itemgetter

def analyze_calc_functions(results_file):
    # Read the results file
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Create list to store website stats
    website_stats = []
    
    # Process each website's results
    for site in results:
        url = site['url']
        chrome_count = site['chrome']['css_function_score']['calc_functions']['count']
        firefox_count = site['firefox']['css_function_score']['calc_functions']['count']
        
        # Take the maximum count between browsers
        max_count = max(chrome_count, firefox_count)
        
        website_stats.append({
            'website': url,
            'calc_count': max_count,
            'chrome_count': chrome_count,
            'firefox_count': firefox_count
        })
    
    # Sort websites by calc function count in descending order
    sorted_stats = sorted(website_stats, key=itemgetter('calc_count'), reverse=True)
    
    # Print results
    print("\nWebsites ranked by number of calc() functions:")
    print("=" * 70)
    print(f"{'Rank':<6}{'Website':<40}{'Max':<8}{'Chrome':<8}{'Firefox':<8}")
    print("-" * 70)
    for i, stat in enumerate(sorted_stats, 1):
        print(f"{i:<6}{stat['website']:<40}{stat['calc_count']:<8}{stat['chrome_count']:<8}{stat['firefox_count']:<8}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_calc.py <results_file>")
        sys.exit(1)
    analyze_calc_functions(sys.argv[1])
