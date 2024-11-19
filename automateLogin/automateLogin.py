#https://auth.flattrade.in/?app_key=cb95baef93fa48bb8dd39642a77bb6bb


import time
import pyotp
from urllib.parse import parse_qs, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

# Path to your ChromeDriver executable
chrome_driver_path = "C:/WebDriver/chromedriver.exe"

# Create a Service object and pass it to Chrome
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

URL = "https://auth.flattrade.in/?app_key="
USERID = "FT053455"
PWD = "Deepak@94"
factor = 'QA622YDDQD2DXH7F27A25F6DWU33AR2V'
totp = pyotp.TOTP(factor)


def autoLogin(key):
    # Open a webpage
    global URL
    URL = URL + key
    driver.get(URL)
    # Locate the input fields and fill them in
    try:
        user_id_input = driver.find_element(By.XPATH, "//label[text()='User ID']/following-sibling::input")

        # Now you can interact with the located input field
        user_id_input.send_keys(USERID)



        user_pwd_input = driver.find_element(By.XPATH, "//label[text()='Password']/following-sibling::input")

        # Now you can interact with the located input field
        user_pwd_input.send_keys(PWD)
        
        
        
        
        # Generate the current TOTP code
        current_otp = totp.now()
        
        user_otp_input = driver.find_element(By.XPATH, "//label[text()='TOTP/OTP']/following-sibling::input")

        # Now you can interact with the located input field
        user_otp_input.send_keys(current_otp)


        # Submit the form by clicking the submit button
        # Using XPath to find the button with type 'button' and text 'Login'
        login_button = driver.find_element(By.XPATH, "//button[@type='button' and @id='sbmt']")

        # Now you can interact with the located button
        login_button.click()

        
        # Wait for the page to load (adjust sleep time as needed)
        time.sleep(3)
        
        # Get the new URL after redirection
        new_url = driver.current_url
        print("Redirected URL:", new_url)
        driver.quit()
              # Parse the URL
        parsed_url = urlparse(new_url)

        # Extract query parameters
        query_params = parse_qs(parsed_url.query)

        # Get the value of 'code'
        code_value = query_params.get('code', [None])[0]

        print(f"Code value: {code_value}")
        return code_value
    except Exception as e:
        # Close the driver
        print('quit')
        driver.quit()
    
    
    
    
