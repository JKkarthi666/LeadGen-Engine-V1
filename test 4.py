import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# ========== Code 2 Functions (Unchanged) ==========

def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def random_human_touch(driver):
    try:
        for _ in range(random.randint(2, 4)):
            amount = random.randint(100, 250)
            driver.execute_script(f"window.scrollBy(0, {amount});")
            time.sleep(random.uniform(0.3, 0.6))

        elements = driver.find_elements(By.CSS_SELECTOR, "div.accordion-wrapper div.accordion")
        if elements:
            target = random.choice(elements)
            ActionChains(driver).move_to_element(target).perform()
            time.sleep(random.uniform(0.5, 1.2))
    except Exception as e:
        print("Random touch error:", e)

def click_all_accordions_and_extract(driver):
    data = {}
    random_human_touch(driver)
    accordion_headers = driver.find_elements(By.CSS_SELECTOR, "div.accordion-wrapper div.accordion")

    for index, header in enumerate(accordion_headers):
        section_title = header.text.strip()

        if index == 0:
            print(f"✅ Skipping click for: {section_title} (already open)")
        else:
            try:
                ActionChains(driver).move_to_element(header).perform()
                time.sleep(random.uniform(0.8, 1.4))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", header)
                time.sleep(random.uniform(0.5, 1.0))
                driver.execute_script("arguments[0].click();", header)
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, f"//div[contains(@class,'accordion') and contains(text(), '{section_title}')]/following-sibling::div[1]")
                    )
                )
            except Exception as e:
                data[section_title + " ERROR"] = f"Click failed: {str(e)}"
                continue

        try:
            panel_xpath = f"//div[contains(@class,'accordion') and contains(text(), '{section_title}')]/following-sibling::div[1]"
            panel = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, panel_xpath))
            )
            section_data = {}
            items = panel.find_elements(By.CSS_SELECTOR, "li")
            for li in items:
                try:
                    title = li.find_element(By.CSS_SELECTOR, "span.title").text.strip()
                    value = li.find_element(By.CSS_SELECTOR, "span.value").text.strip()
                    section_data[title] = value
                    time.sleep(random.uniform(0.05, 0.15))
                except:
                    continue
            data[section_title] = section_data
        except Exception as e:
            data[section_title + " ERROR"] = f"Data scrape failed: {str(e)}"
        time.sleep(random.uniform(0.7, 1.3))

    return data

def scrape_caravan_details(url):
    driver = setup_driver()
    driver.get(url)

    result = {"URL": url}

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.title"))
        )

        random_human_touch(driver)

        result["Title"] = driver.find_element(By.CSS_SELECTOR, "h1.title").text
        result["Model Number"] = driver.find_element(By.CSS_SELECTOR, "p.chassis").text
        result["Retail Price"] = driver.find_element(By.CSS_SELECTOR, "div.price p span").text.strip()
        result["Tow-Away Price"] = driver.find_element(By.CSS_SELECTOR, "div.tow-away p span").text.strip()
        result["Weekly Price"] = driver.find_element(By.CSS_SELECTOR, "div.weekly-price span").text.strip()

        try:
            desc_element = driver.find_element(By.CSS_SELECTOR, "div.caravan-description-wrap.key-specs p")
            result["Description"] = desc_element.text.strip()
        except:
            result["Description"] = "No description found"

        upgrades = []
        for item in driver.find_elements(By.CSS_SELECTOR, "div.options-prices ul li"):
            try:
                name = item.find_element(By.CSS_SELECTOR, "span.name").text.strip()
                price = item.find_element(By.CSS_SELECTOR, "span.price").text.strip()
                upgrades.append(f"{name} {price}")
            except:
                continue
        result["Upgrades"] = "\n".join(upgrades)

        key_specs = {}
        for spec in driver.find_elements(By.CSS_SELECTOR, "ul.key.specifications li"):
            try:
                spec_title = spec.find_element(By.CSS_SELECTOR, "span.title").text.strip()
                spec_value = spec.find_element(By.CSS_SELECTOR, "span.value").text.strip()
                key_specs[spec_title] = spec_value
            except:
                continue
        result["Key Specs"] = str(key_specs)

        result["Primary Image"] = driver.find_element(By.CSS_SELECTOR, "img.slide-bg-img").get_attribute("src")

        secondary_imgs = []
        for img_el in driver.find_elements(By.CSS_SELECTOR, "div.caravan-slider img.caravan-thumb"):
            src = img_el.get_attribute("src")
            if src and src != result["Primary Image"] and src not in secondary_imgs:
                secondary_imgs.append(src)
        result["Secondary Images"] = "\n".join(secondary_imgs)

        accordion_data = click_all_accordions_and_extract(driver)
        result["Accordion Sections"] = str(accordion_data)

        print(f"[DONE] Scraped: {result['Title']}")

    except Exception as e:
        print("Error:", e)
        result["Error"] = str(e)
    finally:
        driver.quit()
        return result

# ========== Code 1 Logic ==========

def get_product_urls():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://snowyriverperth.com.au/in-stock/")
    time.sleep(3)

    try:
        window_width = driver.execute_script("return window.innerWidth;")
        window_height = driver.execute_script("return window.innerHeight;")
        click_x = random.randint(100, window_width - 100)
        click_y = random.randint(100, window_height - 100)

        actions = ActionChains(driver)
        actions.move_by_offset(click_x, click_y).click().perform()
        time.sleep(random.uniform(1.0, 2.0))
        actions.move_by_offset(-click_x, -click_y).perform()
    except Exception as e:
        print(f"Overlay click error: {e}")

    print("Simulating scroll...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_position = 0
    for _ in range(5):
        scroll_position += random.randint(500, 1000)
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(random.uniform(1.5, 3.0))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    time.sleep(2)

    items = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "item"))
    )

    urls = []
    for item in items:
        try:
            link_elem = item.find_element(By.CSS_SELECTOR, "a.btn.btn-default")
            url = link_elem.get_attribute("href")
            if url:
                urls.append(url)
        except:
            continue

    driver.quit()
    return urls

# ========== Runner ==========

if __name__ == "__main__":
    all_urls = get_product_urls()
    all_results = []

    for url in all_urls:
        result = scrape_caravan_details(url)
        all_results.append(result)

    df = pd.DataFrame(all_results)
    df.to_excel("caravan_data.xlsx", index=False)
    print("✅ Data saved to 'caravan_data.xlsx'")
