from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import threading
import os

app = Flask(__name__)

def check_card(card):
    card_data = card.split("|")
    card_number, expiry_month, expiry_year, cvv = card_data

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 25)

    driver.get("https://www.justgiving.com/page/ali-bevans-teamtoby")

    # Selenium işlemleri burada devam edecek...

    driver.quit()

    return "Kart kontrolü tamamlandı: " + card_number

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        card = request.form.get("card")
        if card:
            threading.Thread(target=check_card, args=(card,)).start()
            return jsonify({"status": "İşlem başladı", "card": card})
        return jsonify({"error": "Kart bilgisi yok"})
    return render_template("index.html")

@app.route("/healthz")
def health_check():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
