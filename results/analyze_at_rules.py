#!/usr/bin/env python3
"""
Analyze at-rules in CSS data from results_top5.json.
This script sums all at-rules for each site and lists sites in order of total at-rules.
Uses the maximum count between Chrome and Firefox for each at-rule type.
"""

import json
import sys
from operator import itemgetter

def analyze_at_rules(results_file):
    # Read the results file
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Create list to store website stats
    website_stats = []
    
    # Process each website's results
    for site in results:
        url = site['url']
        site_name = url.replace('https://', '').replace('http://', '')
        
        # Extract at-rules counts for Chrome
        chrome_container = site['chrome']['css_at_rules_score']['container_rules']['count'] if 'chrome' in site and 'css_at_rules_score' in site['chrome'] else 0
        chrome_supports = site['chrome']['css_at_rules_score']['supports_rules']['count'] if 'chrome' in site and 'css_at_rules_score' in site['chrome'] else 0
        chrome_import = site['chrome']['css_at_rules_score']['import_rules']['count'] if 'chrome' in site and 'css_at_rules_score' in site['chrome'] else 0
        chrome_page = site['chrome']['css_at_rules_score']['page_rules']['count'] if 'chrome' in site and 'css_at_rules_score' in site['chrome'] else 0
        
        # Extract at-rules counts for Firefox
        firefox_container = site['firefox']['css_at_rules_score']['container_rules']['count'] if 'firefox' in site and 'css_at_rules_score' in site['firefox'] else 0
        firefox_supports = site['firefox']['css_at_rules_score']['supports_rules']['count'] if 'firefox' in site and 'css_at_rules_score' in site['firefox'] else 0
        firefox_import = site['firefox']['css_at_rules_score']['import_rules']['count'] if 'firefox' in site and 'css_at_rules_score' in site['firefox'] else 0
        firefox_page = site['firefox']['css_at_rules_score']['page_rules']['count'] if 'firefox' in site and 'css_at_rules_score' in site['firefox'] else 0
        
        # Take the maximum count between browsers for each rule type
        max_container = max(chrome_container, firefox_container)
        max_supports = max(chrome_supports, firefox_supports)
        max_import = max(chrome_import, firefox_import)
        max_page = max(chrome_page, firefox_page)
        
        # Calculate total at-rules (sum of maximums)
        total_at_rules = max_container + max_supports + max_import + max_page
        
        # Calculate total for each browser
        chrome_total = chrome_container + chrome_supports + chrome_import + chrome_page
        firefox_total = firefox_container + firefox_supports + firefox_import + firefox_page
        
        # Store the stats
        website_stats.append({
            'website': site_name,
            'total_at_rules': total_at_rules,
            'chrome_total': chrome_total,
            'firefox_total': firefox_total,
            'container_rules': max_container,
            'supports_rules': max_supports,
            'import_rules': max_import,
            'page_rules': max_page
        })
    
    # Sort websites by total at-rules in descending order
    sorted_stats = sorted(website_stats, key=itemgetter('total_at_rules'), reverse=True)
    
    # Print results
    print("\nWebsites ranked by number of at-rules (max of Chrome/Firefox):")
    print("=" * 60)
    print(f"{'Rank':<6}{'Website':<40}{'Total At-Rules':<15}")
    print("-" * 60)
    
    for i, stat in enumerate(sorted_stats, 1):
        print(f"{i:<6}{stat['website']:<40}{stat['total_at_rules']:<15}")
    
    # Calculate total across all sites
    total_all_rules = sum(stat['total_at_rules'] for stat in sorted_stats)
    
    # Print summary
    print("\nTotal at-rules across all sites:", total_all_rules)

if __name__ == "__main__":
    # Default to results_top5.json if no argument is provided
    results_file = sys.argv[1] if len(sys.argv) > 1 else 'results_top5/results_top5.json'
    analyze_at_rules(results_file)
