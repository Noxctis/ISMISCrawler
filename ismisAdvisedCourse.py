from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import getpass
import os

# Configurations
options = Options()
options.headless = False  # Runs browser visibly
options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Disables DevTools logs
ser = Service("./chromedriver.exe")
browser = webdriver.Chrome(service=ser, options=options)

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')  # Clears terminal


# Functions
def load_credentials(file_path="credentials.txt"):
    """Loads credentials from a file."""
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            username = lines[0].strip()
            password = lines[1].strip()
            return username, password
    except FileNotFoundError:
        print("Credentials file not found. Creating a new one...")
        username = input("Enter your username: ")
        password = getpass.getpass("Enter your password: ")
        with open(file_path, "w") as file:
            file.write(f"{username}\n{password}")
        return username, password


def wait_for_element(by, identifier, timeout=5):
    """Waits for an element to be present."""
    return WebDriverWait(browser, timeout).until(EC.presence_of_element_located((by, identifier)))


def check_site_crash_login_page():
    """Checks if the login page is fully loaded by looking for the login button."""
    try:
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn")))
        return False  # No crash, button found
    except TimeoutException:
        print("Login page not loaded properly. Refreshing...")
        return True  # Crash detected


def check_site_crash_after_login():
    """Checks if the homepage is properly loaded by looking for the profile picture."""
    try:
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.ID, "header_profile_pic")))
        return False  # No crash, profile picture found
    except TimeoutException:
        print("Homepage not loaded properly. Refreshing...")
        return True  # Crash detected


def login_attempt(username_input, password_input):
    """Attempts to log into the ISMIS website."""
    browser.get("https://ismis.usc.edu.ph")

    # Ensure the login page is loaded properly
    while check_site_crash_login_page():
        browser.refresh()
        time.sleep(5)

    username = wait_for_element(By.ID, "Username")
    password = wait_for_element(By.ID, "Password")
    login_button = wait_for_element(By.CSS_SELECTOR, "button.btn")

    print("Entering username...")
    username.send_keys(username_input)
    time.sleep(1)
    print("Entering password...")
    password.send_keys(password_input)
    time.sleep(1)
    print(f"Attempting login for {username_input}...")
    login_button.click()


def check_valid_login():
    """Checks if the login is successful."""
    try:
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.validation-summary-errors"))
        )
        print("Wrong username/password. Please try again.")
        return False
    except TimeoutException:
        return True


# def press_block_advising():
#     """Presses the Block Advising button."""
#     try:
#         block_advising_button = wait_for_element(By.CSS_SELECTOR, "a.btn.btn-sm.green.rs-modal[title='Click to see block section list']")
#         block_advising_button.click()
#         print("Block Advising button clicked successfully.")

#         # Wait for the Block Section List to load
#         WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "portlet-title"))
#         )
#         print("Block Section List loaded successfully.")

#         # Fetch href attributes
#         table_body = wait_for_element(By.ID, "BlockSectionBody")
#         links = table_body.find_elements(By.CSS_SELECTOR, "a.green.rs-modal")
#         for link in links:
#             print(link.get_attribute("href"))

#     except TimeoutException:
#         print("Error: Block Section List did not load properly.")
#     except WebDriverException as e:
#         print(f"An error occurred: {e}")

def press_block_advising():
    """Presses the Block Advising button, handles modal issues for 'undefined' or stuck states, and retries indefinitely."""
    while True:
        try:
            # Click the Block Advising button
            block_advising_button = wait_for_element(By.CSS_SELECTOR, "a.btn.btn-sm.green.rs-modal[title='Click to see block section list']")
            block_advising_button.click()
            print("Block Advising button clicked successfully.")

            # Wait for the Block Section List to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "BlockSectionBody"))
            )
            print("Block Section List loaded successfully.")

            # Fetch block titles and href attributes
            block_sections = browser.find_elements(By.CSS_SELECTOR, "#BlockSectionBody h4")
            for block_section in block_sections:
                # Extract block title and link
                title = block_section.text.strip()
                link_element = block_section.find_element(By.CSS_SELECTOR, "a.green.rs-modal")
                link = link_element.get_attribute("href")
                
                print(f"Block Title: {title}")
                print(f"Link: {link}")

            # Break the loop after successful execution
            break

        except TimeoutException:
            print("Error: Block Section List did not load properly. Retrying...")

        except WebDriverException as e:
            # Handle potential modal issues
            try:
                modal = browser.find_element(By.CSS_SELECTOR, "#modal1")
                if modal.is_displayed():
                    modal_body = modal.find_element(By.CSS_SELECTOR, "#modal1Body").text.strip()
                    
                    if "undefined" in modal_body:
                        # Close modal immediately for "undefined"
                        print(f"Modal issue detected: {modal_body}. Closing modal and retrying...")
                        ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                        print("Modal closed due to 'undefined'. Retrying immediately...")
                        continue
                    
                    if "... i'm still processing your request :)" in modal_body:
                        # Wait 10 seconds before retrying for "still processing"
                        print(f"Modal is processing: {modal_body}. Waiting 10 seconds before retrying...")
                        time.sleep(10)
                        ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                        print("Modal closed after 10-second wait. Retrying...")
                        continue
            except Exception as modal_error:
                print(f"Error while handling modal: {modal_error}")

        time.sleep(2)  # Brief delay before retrying


def press_view_lacking():
    """Presses the View Lacking button."""
    try:
        view_lacking_button = wait_for_element(By.CSS_SELECTOR, "a.btn.btn-sm.green.rs-modal[title='Click To Show Lacking Courses.']")
        view_lacking_button.click()
        print("View Lacking button clicked successfully.")
        
        # Wait for the View Lacking List to load
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.portlet-title > h3"))
            )
        print("View Lacking List loaded successfully.")
    except TimeoutException:
        print("Error: View Lacking button not found.")


def press_advised_course():
    """Presses the Advised Course button, handles modal issues for 'undefined' or stuck states, and retries indefinitely."""
    while True:
        try:
            # Click the Advised Course button
            advised_course_button = wait_for_element(By.CSS_SELECTOR, "a.btn.btn-sm.green.rs-modal[title='Click To Show Courses']")
            advised_course_button.click()
            print("Advised Course button clicked successfully.")

            # Wait for the page or content to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "ChooseToAdviseBody"))
            )
            print("Advised Course content loaded successfully.")

            # Break the loop after successful execution
            break

        except TimeoutException:
            print("Error: Advised Course content did not load properly. Retrying...")

        except WebDriverException as e:
            # Handle potential modal issues
            try:
                modal = browser.find_element(By.CSS_SELECTOR, "#modal1")
                if modal.is_displayed():
                    modal_body = modal.find_element(By.CSS_SELECTOR, "#modal1Body").text.strip()
                    
                    if "undefined" in modal_body:
                        # Close modal immediately for "undefined"
                        print(f"Modal issue detected: {modal_body}. Closing modal and retrying...")
                        ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                        print("Modal closed due to 'undefined'. Retrying immediately...")
                        continue
                    
                    if "... i'm still processing your request :)" in modal_body:
                        # Wait 10 seconds before retrying for "still processing"
                        print(f"Modal is processing: {modal_body}. Waiting 10 seconds before retrying...")
                        time.sleep(10)
                        ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                        print("Modal closed after 10-second wait. Retrying...")
                        continue
            except Exception as modal_error:
                print(f"Error while handling modal: {modal_error}")

        time.sleep(2)  # Brief delay before retrying


def navigate_to_block_advising():
    """Navigates to the Block Advising section."""
    browser.get("https://ismis.usc.edu.ph/advisedcourse")

    # Ensure the page is loaded
    while check_site_crash_after_login():
        browser.refresh()
        time.sleep(5)

    # Click the Block Advising button
    press_block_advising()

def navigate_to_view_lacking():
    """Navigates to the View Lacking section."""
    browser.get("https://ismis.usc.edu.ph/advisedcourse")

    # Ensure the page is loaded
    while check_site_crash_after_login():
        browser.refresh()
        time.sleep(5)

    # Click the Block Advising button
    press_view_lacking()

    
def navigate_to_advise_course():
    """Navigates to the Advised Course section and verifies it has loaded properly."""
    browser.get("https://ismis.usc.edu.ph/advisedcourse")

    # Ensure the page is loaded
    while check_site_crash_after_login():
        browser.refresh()
        time.sleep(5)

    # Click the Advised Course button
    press_advised_course()


def main():
    """Main function to control the flow of the program."""
    clear()
    print("Welcome to ISMIS Crawler!\n")
    print("Delivering your information without the hassle.")
    time.sleep(1)
    print("Loading...")

    # Load credentials from a file
    username_input, password_input = load_credentials()

    # Login process
    login_status = False
    while not login_status:
        #clear()
        login_attempt(username_input, password_input)
        login_status = check_valid_login()

    print("Logged in successfully.")

    # Continuously monitor post-login page for crashes
    while check_site_crash_after_login():
        browser.refresh()
        time.sleep(5)

    # Demonstrate button interactions
    #print("Navigating to Block Advising...")
    #time.sleep(10)
    #navigate_to_block_advising()

    #print("Navigating to View Lacking...")
    #navigate_to_view_lacking()

    print("Navigating to Advised Course...")
    navigate_to_advise_course()

    print("DONE!")
    # Keep the browser open after navigation
    input("Press Enter to exit and close the browser.")
    browser.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.quit()