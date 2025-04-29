from selenium import webdriver

import time
import json

def collect_requests(driver, url):
    """
    Visits the page and collects network request URLs.
    """
    driver.get(url)
    time.sleep(3)  # Allow resources to load

    logs = driver.get_log('performance')
    requested_urls = set()

    for entry in logs:
        message = entry.get('message')
        if message:
            try:
                msg = json.loads(message)['message']
                if msg['method'] == 'Network.requestWillBeSent':
                    url_requested = msg['params']['request']['url']
                    requested_urls.add(url_requested)
            except Exception:
                continue

    return requested_urls