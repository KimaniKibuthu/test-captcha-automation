import logging
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from solve_captcha import CaptchaSolver

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

if __name__ == "__main__":
    try:
        logger.info("Initializing WebDriver...")
        driver = webdriver.Chrome()

        logger.info("Navigating to the target webpage...")
        driver.get('https://itax.kra.go.ke/KRA-Portal/complianceMonitoring.htm?actionCode=validateTCC')

        logger.info("Locating the dropdown element...")
        dropdown = Select(driver.find_element(By.NAME, 'certiType'))
        logger.info("Selecting 'Tax Compliance Certificate (TCC)' from the dropdown...")
        dropdown.select_by_visible_text('Tax Compliance Certificate (TCC)')

        logger.info("Locating the Certificate/License Number input field...")
        certificate_input = driver.find_element(By.NAME, 'certiNo')
        logger.info("Entering the Certificate/License Number...")
        certificate_input.send_keys('A009294199J')

        logger.info("Locating CAPTCHA image element...")
        captcha_image = driver.find_element(By.XPATH, '//*[@id="captcha_image"]')
        captcha_src = captcha_image.get_attribute('src')
        logger.info(f"Downloading CAPTCHA image from: {captcha_src}")

        # Download CAPTCHA image
        captcha_response = requests.get(captcha_src)
        if captcha_response.status_code == 200:
            logger.info("CAPTCHA image downloaded successfully.")
            with open("captcha.png", 'wb') as file:
                file.write(captcha_response.content)
            logger.info("CAPTCHA image saved as 'captcha.png'.")
        else:
            logger.error(f"Failed to download CAPTCHA image. Status code: {captcha_response.status_code}")
            driver.quit()
            exit()

        # Attempt to solve CAPTCHA using the custom solver
        logger.info("Attempting to solve CAPTCHA using the custom solver...")
        solver = CaptchaSolver('captcha.png')  # Pass the downloaded image to the solver
        result = solver.solve_captcha()
        captcha_solution = None
        
        if result:
            captcha_solution = result
            logger.info(f"CAPTCHA solved successfully. Solution: {captcha_solution}")
        else:
            logger.error("Failed to solve CAPTCHA automatically. Falling back to manual input...")
            # Fall back to manual CAPTCHA solving
            captcha_solution = input("Please manually solve the CAPTCHA by looking at 'captcha.png' and enter the solution: ")
        
        # Fill in the CAPTCHA solution and submit the form
        logger.info("Entering CAPTCHA solution...")
        captcha_input = driver.find_element(By.NAME, 'captchaText')
        captcha_input.send_keys(captcha_solution)

        logger.info("Submitting the form...")
        submit_button = driver.find_element(By.NAME, 'btnVerifytccCert')
        submit_button.click()

        logger.info("Form submitted successfully.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Closing the WebDriver...")
        driver.quit()

