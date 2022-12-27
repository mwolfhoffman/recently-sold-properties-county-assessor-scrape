from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# TODO: use chromeOptions to avoid loading images and to use disk caching. 
# TODO: read robots.txt 

def main(address, date_sold):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    wait = WebDriverWait(driver, 10)
    # driver.maximize_window()
    driver.get("https://slco.org/assessor/")

    time.sleep(1)
    address_input = driver.find_element(By.ID, "AddressSearch")
    address_input.clear()
    address_input.send_keys(address)

    # Store the ID of the original window
    original_window = driver.current_window_handle

    # Check we don't have other windows open already
    assert len(driver.window_handles) == 1

    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id=\"BeginSearch\"]")))
    driver.execute_script("arguments[0].click();", button)

   # Wait for the new window or tab
    wait.until(EC.number_of_windows_to_be(2))

    # Loop through until we find a new window handle
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break

    parcel_details = driver.page_source

    soup = BeautifulSoup(parcel_details, 'html.parser')

    owner = soup.select_one(
        "#parcelFieldNames > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(2)").text or ""
    owner_enc = owner.encode(encoding='utf8')
    owner_decode = owner_enc.decode('utf8', 'strict')

    market_value = soup.select_one(
        "#valuehistory > table > tbody > tr:nth-child(1) > td:nth-child(5)").text or ""
    market_value_enc = market_value.encode(encoding='utf8')
    market_value_decode = market_value_enc.decode('utf8', 'strict')

    print(
        {
            "owner": owner_decode,
            "address": address,
            "date_sold": date_sold,
            "market_value": market_value_decode
        }
    )

    time.sleep(1)

    driver.quit()


main("1221 W Tamarack Rd", "May 11, 2020")

# parcelFieldNames > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(2)
