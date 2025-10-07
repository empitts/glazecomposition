from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException # Import specific exception type

from PIL import Image
import urllib
import io
import csv

import requests
from selenium.webdriver.support.ui import WebDriverWait
import time
from datetime import datetime
import os
import json
import requests
import urllib3
import pandas as pd

#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#your chrome browser's version of chrome driver zip needs to be installed in the same folder as this script for it to run
#possibly run the command to enable mac to use it even if it is unsecured xattr -d com.apple.quarantine <path>/chromedriver
#chrome driver makes a link between chrome browser and the api
# selenium drivers provide an api to interact with the web browser 
"""
        # the program doesn't have to keep loading the chrome browser
        # make the driver headless to turn off the browser

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
"""

CHROME_DRIVER_PATH = webdriver.ChromeService(executable_path="/Users/EMPITTS/Documents/webscraper/web_bot/chromedriver")
OP = webdriver.ChromeOptions()
OP.add_argument('--headless')
DRIVER = webdriver.Chrome(service = CHROME_DRIVER_PATH)

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.114 Safari/537.36'
REQUEST_HEADER = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US, en;q=0.5',
}

def login():

    try:
        with open('./web_bot/config.json') as configFile:
            credentials = json.load(configFile)
            time.sleep(1)

            for i in range(2):
                element = WebDriverWait(DRIVER, 10).until(
                    ec.presence_of_element_located((By.XPATH, '//*[@id="glazy-app-div"]/header/div[1]/div[2]/div[2]/button'))
                )

                #click login
                DRIVER.find_element(By.XPATH, '//*[@id="glazy-app-div"]/header/div[1]/div[2]/div[2]/button').click()

                time.sleep(1)

                username = DRIVER.find_element(By.ID, 'email')
                username.clear() #input field so clear it
                username.send_keys(credentials["USERNAME"])

                password = DRIVER.find_element(By.NAME, 'password')
                password.clear() #input field so clear it
                password.send_keys(credentials["PASSWORD"])
                
                element = WebDriverWait(DRIVER, 10).until(
                    ec.presence_of_element_located((By.XPATH, '//*[@id="glazy-app-div"]/header/div[2]/div/div[2]/div/div/div/div/div[3]/form/div[3]/button'))
                )
                element.click()
                time.sleep(1)

                DRIVER.refresh()

    except WebDriverException as e:
        print(f"Error {e}")


def main():
    try:
        """
            mid fired 4-8
            sorted by best
            top 109 pages of results
        """
        # https://glazy.org/search?base_type=460&cone=mid&p=1&order=best&analysisName=umfAnalysis&photo=true&production=true
        site_url = 'https://www.glazy.org/'
        DRIVER.get("https://glazy.org/search")
        ps = DRIVER.page_source #similar to requests response.text

        data = dict()
        tile_details = dict()
        glazyId = dict()

        login()
        
        # pull up search
        #first 109 pages with: best rating, pictures, production
        DRIVER.get("https://glazy.org/search?base_type=460&cone=mid&p=1&order=best&analysisName=umfAnalysis&photo=true&production=true")
        
        # click extended image view                
        wait = WebDriverWait(DRIVER, 5)
        searchformat = wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/div/div[1]/div/div[1]/div[2]/button[2]')))
        searchformat.click()

        try: 
            """
            for skip in range(1,3):
                # select the next page arrow
                print("skip: ", skip)
                element_button = wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/div/div[1]/div/div[2]/div/nav/button[5]')))
                element_button.click()
            """
            for pg in range(1,110): #109 pages
                print("page: ", pg)
                time.sleep(5)
                for i in range(1,37): # 36 on each page
                    #get recipe
                    wait = WebDriverWait(DRIVER, 10)
                    recipe_card = wait.until(ec.element_to_be_clickable((By.XPATH, f'//*[@id="glazy-app-div"]/div/div[2]/main/div/section/div[{i}]/div')))

                    #get recipe details and id
                    recipe_tags = DRIVER.find_element(By.XPATH, f'//*[@id="glazy-app-div"]/div/div[2]/main/div/section/div[{i}]/div/div[2]/div[1]/div/div[1]')
                    materials_html = DRIVER.find_element(By.XPATH, f'//*[@id="glazy-app-div"]/div/div[2]/main/div/section/div[{i}]/div/div[2]/div[2]')

                    e = recipe_tags.find_elements(By.XPATH, './/*')
                    id = e[0].text[1:]
                    tag = e[1].text
                    firing = e[2].text[1:]

                    print(id)

                    scrapedDict = dict({
                        "firing": firing, 
                        "tag": tag,
                        "details": materials_html.text
                    })
                    glazyId[id] = scrapedDict

                # select the next page arrow
                wait = WebDriverWait(DRIVER, 10)
                page_list = wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/div/div[1]/div/div[2]/div/nav')))
                next_arrow = page_list.find_elements(By.XPATH, './/*')
                next_arrow[-2].click()

            #print(glazyId) //*[@id="glazy-app-div"]/div/div[2]/main/div/section/div[36]/div

        except WebDriverException as e:  # Catch specific Selenium WebDriver exceptions

            print(f"An error occurred: {e}")  # Print the error message
            input("press any key...")
        except Exception as e:
            print(e)
            input("press any key2...")

        #save dictionary into pkl file with date
        df = pd.DataFrame(glazyId)
        dt = datetime.now().strftime("%Y%m%d_%H%M%S")

        df.to_pickle(f'glazy_id_lists_top_production_{dt}.pkl')

        print(f"\nDataFrame saved to 'glazy_id_lists_top_production_{dt}.pkl'")

        # Load the DataFrame from the pickle file
        #loaded_df = pd.read_pickle(f'glazy_id_lists_top_production_{dt}.pkl')
        #print(loaded_df)

        #DRIVER.get_screenshot_as_file('/path/and/filename')
        #element = DRIVER.find_element(By.XPATH, '//')

        # get the href for an element that has an href attribute 
        #element[0].get_attribute("href")


        #static search will be faster vs dynamic with selenium

        #Driver can have an implicit wait: it will wait up to x seconds to finish loading vs sleep
        # it continues once it finishes loading

        # waiting for specific elements to be visible so we can interract with it
        #selenium.webdriver.common.by, ui WebDriverWait, expected conditions

        #wait = WebDriverWait(DRIVER,10) #load for up to 10 seconds
        #xPath = '//*[@id="data-util-col"]/section[2]/table/tbody/tr[1]'
        #keep logic in a try except
        #wait.until(ec.visibility_of_element_located(By.XPATH,xPath))
        #elem = DRIVER.find_element(By.XPATH, xPath)
        #the driver wont error out until the element given is visable

        #you might have to wait for a more specific xpath to make sure the slowest elements have loaded and search after it loads

        # We can continuously poll the site if it had updating information
        """
        saveEvery = 30
        While True:
            try:
                elem = DRIVER.find_elements()
            except:
            
            #save it to a file as it goes
        """
        #inputEle = DRIVER.find_element(By.ID, "").click

        #inputEle.send_keys("whooo")
        #inputEle.submit()



    except Exception as e:
        print(e)
        DRIVER.close()
    

if __name__ == "__main__":
    main()
