"""
╔══════════════════╗
              TEAMDEV
╚══════════════════╝

[ PROJECT   ]  TeamDev AIO (All-In-One Downloader)
[ DEVELOPER ]  @MR_ARMAN_08

────────────────────

[ SUPPORT   ]  https://t.me/Team_X_Og
[ UPDATES   ]  https://t.me/TeamDevXBots
[ ABOUT US  ]  https://TeamDev.sbs

────────────────────

[ DONATE    ]  https://Pay.TeamDev.sbs

────────────────────
      FAST • POWERFUL • ALL-IN-ONE
      
"""

import threading
import time
from bs4 import BeautifulSoup

_driver = None
_lock = threading.Lock()


def get_driver():
    global _driver
    with _lock:
        if _driver is None:
            from seleniumbase import Driver
            _driver = Driver(
                uc=True,
                headless=True,
                incognito=True,
                no_sandbox=True,
                disable_gpu=True,
                chromium_arg="--disable-dev-shm-usage,--no-sandbox"
            )
            print("✅ CGpt Driver started")
        return _driver


def quit_driver():
    global _driver
    with _lock:
        if _driver:
            try:
                _driver.quit()
            except:
                pass
            _driver = None


def chat_gpt(prompt: str):
    driver = get_driver()
    try:
        driver.get("https://chatgpt.com")
        time.sleep(5)

        selectors = [
            'textarea#prompt-textarea',
            'textarea[data-id="prompt-textarea"]',
            'div[role="textbox"]'
        ]

        input_box = None
        for sel in selectors:
            try:
                input_box = driver.find_element("css selector", sel)
                if input_box:
                    break
            except:
                continue

        if not input_box:
            return None, "input_box_not_found"

        input_box.clear()
        input_box.send_keys(prompt)

        try:
            btn = driver.find_element("css selector", 'button[data-testid="send-button"]')
            btn.click()
        except:
            input_box.send_keys("\n")

        time.sleep(6)
        for _ in range(10):
            time.sleep(2)
            if not driver.find_elements("css selector", 'button[aria-label*="Stop" i]'):
                break

        response = ""
        resp_selectors = [
            'div[data-message-author-role="assistant"] div.markdown',
            'div.markdown.prose'
        ]

        for sel in resp_selectors:
            try:
                elems = driver.find_elements("css selector", sel)
                if elems:
                    response = elems[-1].text
                    if response.strip():
                        break
            except:
                continue

        if not response.strip():
            soup = BeautifulSoup(driver.page_source, "html.parser")
            blocks = soup.find_all("div", {"data-message-author-role": "assistant"})
            if blocks:
                response = blocks[-1].get_text(strip=True)

        text = response.strip()
        if not text:
            return None, "no_response"

        return {"response": text}, None

    except Exception as e:
        quit_driver()
        return None, str(e)


def generate_image(prompt: str):
    driver = get_driver()
    try:
        driver.get("https://deepai.org/machine-learning-model/text2img")
        time.sleep(6)

        input_box = driver.find_element("css selector", "textarea, input[type='text']")
        input_box.clear()
        input_box.send_keys(prompt)

        try:
            btn = driver.find_element("css selector", "button[type='submit']")
            btn.click()
        except:
            input_box.send_keys("\n")

        time.sleep(12)

        img_link = ""
        try:
            img = driver.find_element("css selector", "#main-image")
            img_link = img.get_attribute("src")
        except:
            pass

        if not img_link:
            return None, "image_not_found"

        return {"image_url": img_link}, None

    except Exception as e:
        quit_driver()
        return None, str(e)
