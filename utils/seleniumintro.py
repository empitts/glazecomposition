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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


import pandas as pd

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
    with open('./web_bot/config.json') as configFile:
        credentials = json.load(configFile)
        print(credentials)
        time.sleep(1)
        DRIVER.find_element(By.XPATH, value="//a[text()='Log in']").click()
        time.sleep(2)

        username = DRIVER.find_element(By.CSS_SELECTOR, value="input[name='username']")
        username.clear() #input field so clear it
        username.send_keys(credentials["USERNAME"])
        
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
        DRIVER.get("https://www.glazespectrum.com/")
        #DRIVER.get("https://glazy.org/recipes/646321")
        ps = DRIVER.page_source #similar to requests response.text

        #find elements by xpath, find by id,etc...
        #elem = DRIVER.find_element(By.ID, '')
        #elem2 = DRIVER.find_element(By.XPATH, '//...') #in inspect get xpath by copy>xpath
        #may need to fix 
        h = ["Clay", "Firing", "Recipe", "Adjustments", "Source", "Notes", "ImageFilename"]
        site_url = 'https://www.glazespectrum.com/'

        image_src_urls = []
        data = dict()
        tile_details = dict()

        # //*[@id="tiles"]/button[33]
        # //*[@id="tiles"]/button[42]/img //*[@id="tiles"]/button[461]/img
        time.sleep(7)
        tile = DRIVER.find_element(By.XPATH, '//*[@id="tiles"]/button[457]').click()

        try: 
            for i in range(455,463): #357):
                time.sleep(1)

                tile_images = DRIVER.find_element(By.XPATH, f'/html/body/div[4]/div[2]/div/div[1]/img[{1}]')
                tile_table = DRIVER.find_element(By.CLASS_NAME, 'recipe-container')

                """
                for tr in DRIVER.find_elements(By.XPATH, '/html/body/div[4]/div[2]/div/div[2]/div[1]/table/tbody'):
                    tds = tr.find_elements(By.TAG_NAME, 'td')
                    if tds: 
                        tile_details.append([td.text for td in tds])
                """

                imageFile = tile_images.get_attribute('src')
                image_src_urls.append(imageFile)
                image_id =  imageFile.split('/')[5]

                name = DRIVER.find_element(By.CLASS_NAME, 'tile-detail-title').text
                id = name.split(' ')[-1]

                clay = DRIVER.find_element(By.CLASS_NAME, 'tile-detail-clay').text
                firing = DRIVER.find_element(By.CLASS_NAME, 'tile-detail-firing').text
                src = DRIVER.find_element(By.CLASS_NAME, 'tile-detail-source').text
                notes = DRIVER.find_element(By.CLASS_NAME, 'tile-detail-notes').text #notes might be empty when they have nothing but the element exists

                recipeDict = dict()
                colourantDict = dict()
                total = 0

                #adj needs to be skipped if the style=display: none (element copies previous entry)
                adj_html = DRIVER.find_element(By.CLASS_NAME, 'tile-detail-adjustments-row') 
                if not "display: none" in adj_html.get_attribute("style"):
                    adj_html = adj_html.find_element(By.CLASS_NAME, 'tile-detail-adjustments')
                    for entry in adj_html.text.split('\n')[0:]:
                        #parse each string to get number amount and ingredient name
                        #rejoin text parts 
                        recipeentry = entry.split(' ')
                        colourantDict[' '.join(recipeentry[1:])] = float(recipeentry[0])


                recipe_html = DRIVER.find_element(By.CLASS_NAME, 'tile-detail-recipe')
                #skip title
                for entry in recipe_html.text.split('\n')[1:]:
                    #parse each string to get number amount and ingredient name
                    #rejoin text parts 
                    recipeentry = entry.split(' ')
                    try:
                        total = total + float(recipeentry[0])
                        if total > 100:
                            colourantDict[' '.join(recipeentry[1:])] = float(recipeentry[0])
                        else:
                            recipeDict[' '.join(recipeentry[1:])] = float(recipeentry[0])
                    except:
                        notes = notes + " " + str(recipeentry)
                    
                print(i)
                print(image_id)
                print(colourantDict)


                data[id] = {"Clay" : clay, "Firing": firing, "Recipe": recipeDict, "Colourants": colourantDict, "Source": src, "Notes": notes, "ImageFilename": image_id, "SourceUrl": imageFile}

                # /html/body/div[4]/div[2]/div/div[1]/div[3]

                wait = WebDriverWait(DRIVER, 10)
                element = wait.until(ec.invisibility_of_element_located((By.CLASS_NAME, 'tile-image-loading')))
                element_button = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'tile-next')))
                element_button.click()

        except WebDriverException as e:  # Catch specific Selenium WebDriver exceptions

            print(f"An error occurred: {e}")  # Print the error message

        #save dictionary into pkl file with date
        df = pd.DataFrame(data)
        dt = datetime.now().strftime("%Y%m%d_%H%M%S")

        df.to_pickle(f'spectrum_{dt}.pkl')

        print(f"\nDataFrame saved to 'spectrum_{dt}.pkl'")

        # Load the DataFrame from the pickle file
        # loaded_df = pd.read_pickle('spectrum.pkl')

        try: 
            #Content of the image will be a url
            for tiles in image_src_urls:

                img_content = requests.get(tiles,
                                           headers=REQUEST_HEADER,
                                           verify=False).content
                time.sleep(2)

                #Get the bytes IO of the image
                img_file = io.BytesIO(img_content)

                #Stores the file in memory and convert to image file using Pillow
                image = Image.open(img_file)

                file_name = tiles.split('/')[5]
                file_pth = './testTiles/' + file_name

                with open(file_pth, 'wb') as file:
                    image.save(file, 'JPEG')

            input("press any key...")
            DRIVER.close()
        except Exception as e:
            print(e)


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
