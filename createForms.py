from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from loadconfig import loadDefaultConfig

def createSection(driver, title:str, desc:str|None=None):
    add_section_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and @aria-label="Añadir sección"]'))
    )

    # Click the button
    driver.execute_script("arguments[0].click();", add_section_btn)


    title_box = driver.find_elements(By.XPATH, './/div[@aria-label="Título de la sección (opcional)"]')[-1]
    title_box.clear()
    title_box.send_keys(title)

    if desc is not None:
        desc_box = driver.find_elements(By.XPATH, './/div[@aria-label="Descripción (opcional)"]')[-1]
        desc_box.clear()
        desc_box.send_keys(desc)

    return True

def createTextBox(driver, title:str, desc:str|None=None):
    add_section_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and @aria-label="Añadir título y descripción"]'))
    )

    # Click the button
    driver.execute_script("arguments[0].click();", add_section_btn)


    title_box = driver.find_elements(By.XPATH, './/div[@aria-label="Título"]')[-1]
    title_box.clear()
    title_box.send_keys(title)

    if desc is not None:
        desc_box = driver.find_elements(By.XPATH, './/div[@aria-label="Descripción (opcional)"]')[-1]
        desc_box.clear()
        desc_box.send_keys(desc)

    return True


def set_input_value_safe(driver, xpath, text, retries=5, wait_time=0.2):
    """Locate input and set value via JS, retrying if stale element occurs."""
    for _ in range(retries):
        try:
            input_elem = driver.find_elements(By.XPATH, xpath)[-1]
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                arguments[0].blur();
            """, input_elem, text)
            return True
        except StaleElementReferenceException:
            time.sleep(wait_time)
    raise Exception(f"Could not set input value for {xpath}")


def fill_options(driver, options):
    # Rest of the options
    for text in options[1:]:
        set_input_value_safe(driver, './/input[@aria-label="Añadir opción"]', text)
        time.sleep(0.2)  # allow DOM to stabilize
    set_input_value_safe(driver, './/input[@value="Opción 1"]', options[0])
    time.sleep(0.2)

def createQuestion(driver,title:str,opciones:list[str]):
    # Wait for the "Añadir pregunta" button
    add_question_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and @aria-label="Añadir pregunta"]'))
    )

    time.sleep(0.5)

    # Click the button
    add_question_btn.click()

    time.sleep(0.5)

    wait = WebDriverWait(driver, 15)

    # Última caja de pregunta
    question_box = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, './/div[@aria-label="Pregunta"]'))
    )[-1]
    question_box.send_keys(title)

    time.sleep(0.5)

    # Click en "Varias opciones"
    span = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//span[text()='Varias opciones']"))
    )[-1]
    span.click()

    time.sleep(0.8)

    # Click en "Casillas"
    span = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//span[text()='Casillas']"))
    )[-1]
    clickable_div = span.find_element(By.XPATH, "./ancestor::div[@role='option']")
    driver.execute_script("arguments[0].scrollIntoView(true);", clickable_div)
    driver.execute_script("arguments[0].click();", clickable_div)

    fill_options(driver, opciones)

def createForms(config):

    chromedriver_path = config["chromedriver_path"]
    user_data_dir = config["chrome_data_dir"]
    forms_data_path = config["forms_data_path"]

    # Setup Chrome options to use your existing profile
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    # Initialize Chrome
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open Google Forms
    driver.get("https://forms.new")

    time.sleep(2)

    # Load JSON from a file
    with open(forms_data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Iterate over sections
    for section_title, questions in data.items():
        # Create section
        # createSection(driver, section_title)
        createTextBox(driver, section_title)
        # Iterate over questions in the section
        for question_title, options in questions.items():
            createQuestion(driver,question_title, options)
    
    print("The forms has been created successfully.")
    time.sleep(5)

if __name__ == "__main__":
    config = loadDefaultConfig()
    createForms(config)