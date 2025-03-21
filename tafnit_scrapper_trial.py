from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Replace 'path/to/chromedriver' with the actual path to your ChromeDriver
service = Service(executable_path=r"C:\Program Files (x86)\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service)

try:
    # Open the target website
    driver.get('https://tafnit.weizmann.ac.il/MENU1/LOGINNoD.CSP')

    # Wait for the username field to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'Username'))
    )

    # Enter the username
    username_field = driver.find_element(By.ID, 'Username')
    username_field.send_keys('michaeka')

    # Enter the password
    password_field = driver.find_element(By.NAME, 'Password')
    password_field.send_keys('Cheerios22@')


    # Wait until the login button is present
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='כניסה למערכת']"))
    )



    # Click the login button
    login_button = driver.find_element(By.XPATH, "//input[@value='כניסה למערכת']")
    login_button.click()

    # # Wait until the button element is present and clickable
    # WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((By.ID, "idTreeview2"))
    # )
    #
    # # Click the button using the image element with id 'idTreeview2'
    # button_to_click = driver.find_element(By.ID, "idTreeview2")
    # button_to_click.click()

    # Wait for the element to be clickable
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='#' and @onclick='dTreeview.o(2);']"))
    )

    # Click the button using XPath
    button_to_click = driver.find_element(By.XPATH, "//a[@href='#' and @onclick='dTreeview.o(2);']")
    button_to_click.click()

finally:
    # You may want to keep the browser open to see the result
    # Comment out the line below to keep it open
    # driver.quit()
    import time
    time.sleep(10)