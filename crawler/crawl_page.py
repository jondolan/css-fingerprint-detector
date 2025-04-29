import os
import requests
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from crawler.create_driver import create_driver

def _crawl_with_browser(url, window_size=None, user_agent=None, browser_type='chrome'):
    driver = create_driver(window_size, user_agent, browser_type)
    css_sources = []  # Will contain full CSS text

    try:
        driver.set_page_load_timeout(20)
        
        driver.get(url)

        # Wait up to 10 seconds for stylesheets or style tags
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "link"))
        )

        # 1. Inline <style> blocks
        styles = driver.find_elements(By.TAG_NAME, 'style')
        for style in styles:
            css_text = style.get_attribute('innerHTML')
            if css_text:
                css_sources.append(css_text)

        # 2. External <link rel="stylesheet">
        links = driver.find_elements(By.XPATH, '//link[@rel="stylesheet"]')
        for link in links:
            href = link.get_attribute('href')
            if href:
                if href.startswith('file://'):
                    # Handle local CSS files
                    try:
                        css_path = href.replace('file://', '')
                        if not css_path.startswith('/'):
                            # Handle relative paths for local files
                            base_dir = os.path.dirname(url.replace('file://', ''))
                            css_path = os.path.join(base_dir, css_path)
                        with open(css_path, 'r') as f:
                            css_sources.append(f.read())
                        logging.info(f"[+] Local CSS file loaded: {css_path}")
                    except Exception as e:
                        logging.error(f"[-] Failed to load local CSS file: {css_path} ({e})")
                elif href.startswith('data:'):
                    # Embedded data URI
                    try:
                        # Split and decode
                        content = href.split(',', 1)[1]
                        css_sources.append(content)
                        logging.info(f"[+] Embedded data URI CSS added directly ({len(content)} bytes)")
                    except Exception as e:
                        logging.error(f"[-] Failed to process data URI CSS: {href} ({e})")
                else:
                    try:
                        resp = requests.get(href, timeout=10)

                        if resp.status_code == 200:
                            content_type = resp.headers.get('Content-Type', '')
                            # Check header first
                            if 'text/css' in content_type:
                                css_sources.append(resp.text)
                            # If not labeled text/css, but looks like CSS anyway
                            elif resp.text.strip().startswith('@') or '{' in resp.text:
                                # Simple heuristic: if the file starts with @import/@font/@container or has CSS blocks
                                logging.warning(f"[!] Non-standard Content-Type, but content looks like CSS: {href}")
                                css_sources.append(resp.text)
                            else:
                                logging.error(f"[-] Content does not look like CSS: {href}")
                        else:
                            logging.error(f"[-] Failed to fetch CSS resource {href} (HTTP {resp.status_code})")

                    except Exception as e:
                        logging.error(f"[-] Error fetching external CSS {href}: {e}")

    except Exception as e:
        logging.error(f"[-] Error crawling {url} with {browser_type}: {e}")
    
    finally:
        driver.quit()

    return css_sources

def crawl_single_page(url, window_size=None, user_agent=None):
    """
    Crawls a single page with both Chrome and Firefox browsers.
    
    Args:
        url (str): URL to crawl. Can be either:
            - http(s):// URL for web pages
            - file:// URL for local HTML files
        window_size (tuple, optional): Browser window size as (width, height)
        user_agent (str, optional): Custom user agent string
    
    Returns:
        dict: Results for each browser containing CSS sources. Format:
            {
                'chrome': [css_source1, css_source2, ...],
                'firefox': [css_source1, css_source2, ...]
            }
            
    Note:
        For file:// URLs, relative paths in <link> tags are resolved relative to 
        the HTML file's location. The file:// URL should be in the format:
        file:///absolute/path/to/file.html
    """
    results = {
        'chrome': [],
        'firefox': []
    }
    
    # Crawl with Chrome
    logging.info(f"Crawling {url} with Chrome")
    try:
        results['chrome'] = _crawl_with_browser(url, window_size, user_agent, 'chrome')
    except Exception as e:
        logging.error(f"Failed to crawl {url} with Chrome: {str(e)}")
    
    # Crawl with Firefox
    logging.info(f"Crawling {url} with Firefox")
    try:
        results['firefox'] = _crawl_with_browser(url, window_size, user_agent, 'firefox')
    except Exception as e:
        logging.error(f"Failed to crawl {url} with Firefox: {str(e)}")
    
    return results
