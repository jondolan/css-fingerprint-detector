from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def create_driver(window_size="1920,1080", user_agent=None, browser_type='chrome'):
    if window_size is None:
        window_size = "1920,1080"  # default window size

    if browser_type.lower() == 'chrome':
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--window-size={window_size}")

        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")

        caps = DesiredCapabilities.CHROME.copy()
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options,
        )
    else:  # firefox
        options = FirefoxOptions()
        options.add_argument("--headless")
        
        # Parse window size
        width, height = window_size.split(',')
        options.add_argument(f"--width={width}")
        options.add_argument(f"--height={height}")

        if user_agent:
            options.set_preference("general.useragent.override", user_agent)

        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=options,
        )

    driver.set_page_load_timeout(10)  # seconds
    return driver
