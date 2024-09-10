import cv2
import pytesseract
import logging
import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
import helper

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def solve_math_captcha(image_path):
    """Solve a mathematical CAPTCHA using helper methods."""
    try:
        text = helper.process_image(image_path)
        result = helper.process_text(text)
        logger.info(f"CAPTCHA detected: {text}, Response: {result}")
        
        # Ask the user to verify the detected text
        user_input = input(f"Is the detected CAPTCHA and response correct? (y/n) -> {text}: ")
        if user_input.lower() == 'n':
            # If incorrect, ask the user to input the correct text
            result = input("Please enter the correct CAPTCHA: ")
        logger.info(f"CAPTCHA solved successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Error solving CAPTCHA: {e}")
        return None


def set_certificate_type(driver):
    """Select the certificate type from a dropdown menu."""
    try:
        certi_type_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "certiType"))
        )
        certi_type_dropdown.click()
        certi_type_dropdown.find_element(By.XPATH, '//option[@value="T"]').click()
        logger.info("Certificate type selected successfully.")
    except Exception as e:
        logger.error(f"Error selecting certificate type: {e}")


def download_captcha_image(captcha_src):
    """Download the CAPTCHA image from the given source URL."""
    try:
        response = requests.get(captcha_src)
        if response.status_code == 200:
            captcha_path = "captcha.png"
            with open(captcha_path, 'wb') as file:
                file.write(response.content)
            logger.info(f"CAPTCHA image downloaded: {captcha_path}")
            return captcha_path
        else:
            logger.error(f"Failed to download CAPTCHA image. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error downloading CAPTCHA image: {e}")
    return None


def handle_alert(driver):
    """Handle JavaScript alert or confirmation dialog."""
    try:
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert.accept()
        logger.info("Alert accepted successfully.")
    except Exception as e:
        logger.error(f"Error handling alert: {e}")


def extract_key_value_pairs(driver):
    """Extract key-value pairs from the result container and return as JSON."""
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[3]/div[3]/table/tbody/tr/td/div/div[3]/table/tbody/tr[2]/td/fieldset/table/tbody'))
        )
        data = {
            row.find_element(By.XPATH, './/td[1]').text.strip(): row.find_element(By.XPATH, './/td[2]').text.strip()
            for row in container.find_elements(By.XPATH, './/tr')
        }
        return json.dumps(data, indent=4)
    except Exception as e:
        logger.error(f"Error extracting key-value pairs: {e}")
        return json.dumps({"error": str(e)})


def initialize_webdriver():
    """Initialize and return a WebDriver instance with custom options."""
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Chrome(options=options)


def main():
    try:
        driver = initialize_webdriver()
        logger.info("Navigating to iTax KRA portal...")
        driver.get('https://itax.kra.go.ke/KRA-Portal/main.htm?actionCode=showOnlineServicesHomeLnclick#')

        # Click button to navigate to next page
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@onclick='javascript:showTCCChecker();']"))
        )
        button.click()

        # Wait for the form field
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'certiNo')))

        set_certificate_type(driver)

        # Input certificate number
        logger.info("Entering Certificate/License Number...")
        certificate_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'certiNo'))
        )
        certificate_input.send_keys('KRAWON1385907724')

        # Download and solve CAPTCHA
        captcha_image = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="captcha_img"]'))
        )
        captcha_src = captcha_image.get_attribute('src')
        captcha_image_path = download_captcha_image(captcha_src)
        time.sleep(10)

        if captcha_image_path:
            captcha_solution = solve_math_captcha(captcha_image_path)
            logger.info("Entering CAPTCHA solution...")
            captcha_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'captcahText'))
            )
            captcha_input.send_keys(str(captcha_solution))

            # Submit the form
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, 'btnVerifytccCert'))
            )
            submit_button.click()

            time.sleep(10)
            handle_alert(driver)

            # Extract and print the result
            json_result = extract_key_value_pairs(driver)
            print(json_result)
        else:
            logger.error("Failed to solve CAPTCHA. Exiting.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Closing the WebDriver...")
        driver.quit()


if __name__ == "__main__":
    main()
