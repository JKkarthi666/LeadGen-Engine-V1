import time
import random
import logging
import pandas as pd

from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium_stealth import stealth

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


# =========================================
# LOGGING
# =========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =========================================
# DRIVER SETUP
# =========================================

def create_driver():

    options = Options()

    options.add_argument("--start-maximized")

    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_argument("--no-sandbox")

    options.add_argument("--disable-dev-shm-usage")

    options.add_argument(
        "user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL",
        fix_hairline=True,
    )

    driver.set_page_load_timeout(60)

    return driver


# =========================================
# HUMAN SIMULATION
# =========================================

def human_behavior(driver):

    try:

        for _ in range(random.randint(3, 6)):

            scroll_amount = random.randint(300, 900)

            driver.execute_script(
                f"window.scrollBy(0, {scroll_amount});"
            )

            time.sleep(random.uniform(0.5, 1.5))

        body = driver.find_element(By.TAG_NAME, "body")

        ActionChains(driver)\
            .move_to_element(body)\
            .perform()

    except Exception as e:

        logging.warning(f"Human simulation failed: {e}")


# =========================================
# SAFE ELEMENT GETTER
# =========================================

def safe_get_text(parent, selector):

    try:

        return parent.find_element(
            By.CSS_SELECTOR,
            selector
        ).text.strip()

    except:

        return ""


def safe_get_attr(parent, selector, attr):

    try:

        return parent.find_element(
            By.CSS_SELECTOR,
            selector
        ).get_attribute(attr)

    except:

        return ""


# =========================================
# GET PRODUCT URLS
# =========================================

def get_product_urls():

    driver = create_driver()

    urls = []

    try:

        driver.get(
            "https://snowyriverperth.com.au/in-stock/"
        )

        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "item")
            )
        )

        human_behavior(driver)

        items = driver.find_elements(
            By.CLASS_NAME,
            "item"
        )

        for item in items:

            try:

                link = item.find_element(
                    By.CSS_SELECTOR,
                    "a.btn.btn-default"
                )

                href = link.get_attribute("href")

                if href:
                    urls.append(href)

            except:
                continue

        logging.info(f"Collected {len(urls)} URLs")

    except Exception as e:

        logging.error(f"URL collection failed: {e}")

    finally:

        driver.quit()

    return list(set(urls))


# =========================================
# ACCORDION SCRAPER
# =========================================

def extract_accordion_data(driver):

    result = {}

    accordions = driver.find_elements(
        By.CSS_SELECTOR,
        "div.accordion-wrapper div.accordion"
    )

    for accordion in accordions:

        try:

            title = accordion.text.strip()

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                accordion
            )

            time.sleep(random.uniform(0.5, 1.2))

            driver.execute_script(
                "arguments[0].click();",
                accordion
            )

            time.sleep(1)

            panel = accordion.find_element(
                By.XPATH,
                "./following-sibling::div[1]"
            )

            rows = panel.find_elements(By.TAG_NAME, "li")

            section_data = {}

            for row in rows:

                key = safe_get_text(row, "span.title")

                value = safe_get_text(row, "span.value")

                if key:
                    section_data[key] = value

            result[title] = section_data

        except Exception as e:

            logging.warning(
                f"Accordion extraction failed: {e}"
            )

    return result


# =========================================
# PRODUCT SCRAPER
# =========================================

def scrape_product(url):

    driver = create_driver()

    data = {"URL": url}

    try:

        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h1.title")
            )
        )

        human_behavior(driver)

        data["Title"] = safe_get_text(
            driver,
            "h1.title"
        )

        data["Model"] = safe_get_text(
            driver,
            "p.chassis"
        )

        data["Retail Price"] = safe_get_text(
            driver,
            "div.price p span"
        )

        data["Tow Away Price"] = safe_get_text(
            driver,
            "div.tow-away p span"
        )

        data["Weekly Price"] = safe_get_text(
            driver,
            "div.weekly-price span"
        )

        data["Description"] = safe_get_text(
            driver,
            "div.caravan-description-wrap.key-specs p"
        )

        data["Primary Image"] = safe_get_attr(
            driver,
            "img.slide-bg-img",
            "src"
        )

        # Secondary Images

        secondary = []

        images = driver.find_elements(
            By.CSS_SELECTOR,
            "div.caravan-slider img.caravan-thumb"
        )

        for img in images:

            src = img.get_attribute("src")

            if src and src not in secondary:
                secondary.append(src)

        data["Secondary Images"] = "\n".join(secondary)

        # Key Specs

        specs = {}

        spec_rows = driver.find_elements(
            By.CSS_SELECTOR,
            "ul.key.specifications li"
        )

        for row in spec_rows:

            key = safe_get_text(row, "span.title")

            value = safe_get_text(row, "span.value")

            if key:
                specs[key] = value

        data["Key Specs"] = specs

        # Accordion

        data["Accordion Data"] = extract_accordion_data(driver)

        logging.info(f"Scraped: {data['Title']}")

    except Exception as e:

        logging.error(f"Scrape failed: {url} | {e}")

        data["Error"] = str(e)

    finally:

        driver.quit()

    return data


# =========================================
# MAIN RUNNER
# =========================================

def run_scraper():

    urls = get_product_urls()

    all_results = []

    with ThreadPoolExecutor(max_workers=3) as executor:

        futures = {
            executor.submit(scrape_product, url): url
            for url in urls
        }

        for future in as_completed(futures):

            result = future.result()

            all_results.append(result)

    df = pd.DataFrame(all_results)

    df.to_excel(
        "enterprise_caravan_data.xlsx",
        index=False
    )

    logging.info(
        "Saved to enterprise_caravan_data.xlsx"
    )


if __name__ == "__main__":

    run_scraper()
