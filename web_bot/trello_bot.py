from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from datetime import date
import os
import json

#your chrome browser's version of chrome driver zip needs to be installed in the same folder as this script for it to run
#possibly run the command to enable mac to use it even if it is unsecured xattr -d com.apple.quarantine <path>/chromedriver
#chrome driver makes a link between chrome browser and the api
# selenium drivers provide an api to interact with the web browser 

CHROME_DRIVER_PATH = webdriver.ChromeService(executable_path="/Users/EMPITTS/Documents/webscraper/web_bot/chromedriver")
OP = webdriver.ChromeOptions()
OP.add_argument('--headless')
DRIVER = webdriver.Chrome(service = CHROME_DRIVER_PATH)

def login():
    with open('./web_bot/config.json') as configFile:
        credentials = json.load(configFile)
        #credentials["PASSWORD"] # get values from the configfile
        print(credentials)
        time.sleep(1)
        #help use find any element on a webpage with xml expressions
        #with selenium
        DRIVER.find_element(By.XPATH, value="//a[text()='Log in']").click()
        time.sleep(2)

        username = DRIVER.find_element(By.CSS_SELECTOR, value="input[name='username']")
        #password = DRIVER.find_element(By.CSS_SELECTOR, value="input[name='password']")

        username.clear() #input field so clear it
        #password.clear()

        username.send_keys(credentials["USERNAME"])
        #password.send_keys(credentials["PASSWORD"])
        
        DRIVER.find_element(By.CSS_SELECTOR, value="button[type='submit']")
        time.sleep(5)


#find a element's ancestor so you can select it
def navigateToBoard():

    #find the div tag with title bot board, then get the ancestor that is the anchor(a) element
    DRIVER.find_element(By.XPATH, value="//div[@title='{}']/ancestor::a".format('Bot Board')).click()
    time.sleep(5)

#a desendant is at the same tree level as an element (sister elements)

def main():
    try:
        DRIVER.get("https://trello.com")#"https://glazy.org/search?base_type=460&photo=true")
        login()
        navigateToBoard()

        input("press any key...")
        print(DRIVER.find_elements('img'))
        #DRIVER.close()

        DRIVER.get_screenshot_as_file('/path/and/filename')
    except Exception as e:
        print(e)
        DRIVER.close()
    

if __name__ == "__main__":
    main()
