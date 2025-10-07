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
import pickle

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def parse_umf_tables():

    #get numbers from the umf
    # Ratios of everything
    # //*[@id="analysis"]/div[1]/div/div[1]/div[1]/div/div[2]
    umf_div = DRIVER.find_elements(By.XPATH, '//*[@id="analysis"]/div[1]/div/div[1]/div[1]/div/div[2]/div')

    fluxes = umf_div[0].text.split(' ')
    stabilizers = umf_div[2].text.split(' ')
    glass_formers = umf_div[4].text.split(' ')
    other = "" if len(umf_div) < 7 else umf_div[6].text.split(' ')

    # flux ratio and si al ratio
    # //*[@id="analysis"]/div[1]/div/div[1]/div[2]
    ratios = DRIVER.find_elements(By.XPATH, '//*[@id="analysis"]/div[1]/div/div[1]/div[2]/div/div')
    flux_ratio = ratios[0].find_element(By.XPATH, './div[2]').text
    silicia_alu_ratio = ratios[1].find_element(By.XPATH, './div[2]').text

    percent_analysis_dict = dict()
    # %analysis table 
    header = list()
    headers = DRIVER.find_elements(By.XPATH, '//*[@id="analysis"]/div[2]/div/div/table/thead/tr/th')
    for chem in headers[1:-1]:
        header.append(chem.text)

    percent_rows = list()
    table_rows = DRIVER.find_elements(By.XPATH, '//*[@id="analysis"]/div[2]/div/div/table/tbody/tr')
    for row in table_rows:
        col_text = list()
        columns = row.find_elements(By.XPATH, './td')
        for col in columns[:-1]:
            col_text.append(col.text)
        percent_rows.append(col_text)
    
    # take all table data and make a dictionanry for each ingredient's chem analysis
    for r in percent_rows:
        material_dict = dict()
        for h in range(len(header)):
            material_dict[header[h]] = r[h + 1] 
        percent_analysis_dict[r[0]] = material_dict
    #print(percent_analysis_dict)

    DRIVER.find_element(By.XPATH, '//*[@id="analysis"]/div[2]/nav/a[2]').click()

    umf_dict = dict()
    # umf table 
    header = list()
    headers = DRIVER.find_elements(By.XPATH, '//*[@id="analysis"]/div[2]/div/div/table/thead/tr/th')
    for chem in headers[1:-1]:
        header.append(chem.text)

    umf_rows = list()
    table_rows = DRIVER.find_elements(By.XPATH, '//*[@id="analysis"]/div[2]/div/div/table/tbody/tr')
    for row in table_rows:
        col_text = list()
        columns = row.find_elements(By.XPATH, './td')
        for col in columns[:-1]:
            col_text.append(col.text)
        umf_rows.append(col_text)
    
    # take all table data and make a dictionanry for each ingredient's umf analysis
    for r in umf_rows:
        material_dict = dict()
        for h in range(len(header)):
            material_dict[header[h]] = r[h + 1] 
        umf_dict[r[0]] = material_dict
    #print(umf_dict['Silica'])

    return percent_analysis_dict, umf_dict

def download_image_src_and_captions():
    images_dict = dict() #store src to its description
    images_html = DRIVER.find_elements(By.CLASS_NAME, 'keen-slider__slide')
    images2 = DRIVER.find_element(By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div[2]')
    #print(len(images2.find_elements(By.TAG_NAME, 'img')))
    totalImages = len(images_html)

    wait = WebDriverWait(DRIVER, 5)
    time.sleep(1)
    wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div[2]/div[1]/a')))
    images2.find_element(By.XPATH, './div[1]/a').click()

    for i in range(15 if len(images_html) > 15 else len(images_html)):
        src = images_html[i].get_attribute('src')
        #print(src)

        #get description
        caption = DRIVER.find_element(By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div[1]/div[2]')
        
        # wait for image to load before getting image       
        wait = WebDriverWait(DRIVER, 10)
        wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'keen-slider')))

        try: 
            #download image from src to glazy folder
            #Content of the image will be a url
            #print(f"Get image {src}")

            img_content = requests.get(src,
                                        headers=REQUEST_HEADER,
                                        verify=False).content

            #Get the bytes IO of the image
            img_file = io.BytesIO(img_content)

            #Stores the file in memory and convert to image file using Pillow
            image = Image.open(img_file)

            file_name = src.split('/')[-1]
            file_pth = './glazy/' + file_name
            new_name = './glazy/' + file_name[:-4] + '.png'

            with open(file_pth, 'wb') as file:
                print(new_name)
                image.save(new_name)

        except Exception as e:
            print(e)
                                                        # //*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div[2]/div[3]/a/img
                                                        # //*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div[2]/div[2]/a/img
        #print(i)                                        # //*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div[2]/div[11]
        wait.until(ec.element_to_be_clickable((By.XPATH, f'//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div[2]/div[{i + 1}]')))
        images2.find_element(By.XPATH, f'./div[{i + 1}]/a').click()

        images_dict[src] = caption.text.split('\n')

    return totalImages, images_dict

def get_single_image():
    images_dict = dict()
    caption = DRIVER.find_element(By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div/div[2]')
                                                #//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div/div[1]/div[1]/img
    single_image = DRIVER.find_element(By.CLASS_NAME, 'cursor-pointer')
    src = single_image.find_element(By.XPATH, './img').get_attribute('src')
    print(src)

    #get description
                                            #//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div/div[3]

    try: 
        #download image from src to glazy folder
        #Content of the image will be a url
        img_content = requests.get(src,
                                    headers=REQUEST_HEADER,
                                    verify=False).content

        #Get the bytes IO of the image
        img_file = io.BytesIO(img_content)

        #Stores the file in memory and convert to image file using Pillow
        image = Image.open(img_file)

        file_name = src.split('/')[-1]
        file_pth = './glazy/' + file_name
        new_name = './glazy/' + file_name[:-4] + '.png'

        with open(file_pth, 'wb') as file:
            print(new_name)
            image.save(new_name)

    except Exception as e:
        print(e)

    images_dict[src] = caption.text.split('\n')

    return 1, images_dict
        
#create df to track recipes with over 10 images to save to a multi image df pickle 

def main():
    try:
        glazy_list = list()

        # save materials with ids in another df and add to the materials pickle
        # name and material id
        materials = dict()

        #open pickle df with format:
        #id, firing, tag, details
        id_df = pd.read_pickle('remaining_glazy_ids.pkl') #'glazy_id_lists_top_production_20250709_192853.pkl')

        # log into glazy
        try: 
            DRIVER.get("https://glazy.org/search")
            ps = DRIVER.page_source #similar to requests response.text
            #login()
        except WebDriverException as e:  # Catch specific Selenium WebDriver exceptions

            print(f"An error occurred: {e}")  # Print the error message
            input("press any key...")
        
        #for each id get request to that page
        # make drop list index
        indices_to_drop = []
        try:
            for index, row in id_df.iloc[1:500].iterrows():
                print(index)
                DRIVER.get(f"https://glazy.org/recipes/{index}")
                #save data and img src and descriptions for id in new db
                #download first 15 images with descriptions
                # write id to multiple image pickle if it has more than 10 images
                #save all the image src in an image column

                # wait for image to load before getting data       
                wait = WebDriverWait(DRIVER, 10)

                element = wait.until(ec.any_of(
                    ec.presence_of_element_located((By.CLASS_NAME, "keen-slider")),
                    ec.presence_of_element_located((By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div/div[1]/div[1]/img'))
                ))

                # //*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div[1]/div[1]/div[1]/img
                # //*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[2]/div/div/div[1]/div[1]/img
                image_slider = DRIVER.find_elements(By.CLASS_NAME, 'keen-slider')
                image_dict = dict()
                if len(image_slider) == 0:
                    imageCount, image_dict = get_single_image()
                else :
                    wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'keen-slider')))
                                    # id to image src and descriptions and subtitles for each
                    imageCount, image_dict = download_image_src_and_captions()

                glaze_subtype = DRIVER.find_element(By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[1]/div/div/div[1]/div[1]/nav/ol/li[3]/div/a').text
                created_metadata = DRIVER.find_element(By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[1]/div/div/div[1]/div[1]').text.split('\n')
                orton_cone = DRIVER.find_element(By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div[1]/h2').text
                # oxidation, reduction, neutral, wood, salt and soda, raku, luster
                atmospheres = DRIVER.find_element(By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div[2]/div[2]/span').text

                # = DRIVER.find_element(By.XPATH, '')
                tags = DRIVER.find_element(By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[1]/div/div/div[2]')
                status = ""
                surface = ""
                transparency = ""
                country = ""
                description = ""

                for tag in tags.find_elements(By.XPATH, './div'):
                    # //*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/span

                    if tag.find_elements(By.XPATH,  ".//*[text()='Status']"):
                        status = tag.find_element(By.XPATH, './/div[2]/span').text

                    if tag.find_elements(By.XPATH,  ".//*[text()='Surface']"):
                        surface = tag.find_element(By.XPATH, './/div[2]/span').text

                    if tag.find_elements(By.XPATH,  ".//*[text()='Transparency']"):
                        transparency = tag.find_element(By.XPATH, './/div[2]/span').text

                    if tag.find_elements(By.XPATH,  ".//*[text()='Country']"):
                        country = tag.find_element(By.XPATH, './/div[2]/span').text 

                #translatebutton = DRIVER.find_elements(By.XPATH, '//*[@id="glazy-app-div"]/div/div[2]/main/section/div/div/div[1]/div[1]/div/div/div[3]/div/div/a')
                translatebutton = DRIVER.find_elements(By.XPATH, "//button[contains(text(), 'Translate')]")
                if (translatebutton):
                    translatebutton[0].click()
                ogLang = DRIVER.find_element(By.XPATH, "//div[contains(text(), 'Original Language')]")

                # possibly check that the found element is not the tag list in case of no description...
                description = ogLang.find_element(By.XPATH, 'preceding-sibling::div[1]').text
                #print(description[:30])

                review_html = DRIVER.find_element(By.ID, "reviews-panel")
                reviews = list()
                for review in review_html.find_elements(By.CLASS_NAME, 'prose break-words'):
                    reviews.append(review.text)
                recipe_html = DRIVER.find_element(By.CLASS_NAME, 'print-table-row')
                table_html = DRIVER.find_element(By.XPATH, '//*[@id="analysis"]/div[2]/div/div/table')
                
                #revision_ids = DRIVER.find_element(By.XPATH, '')
                #revision_of_ids = DRIVER.find_element(By.XPATH, '')

                #get tbody html and put ingredients before total in base and after in colourants
                recipe_base = list()
                recipe_colourants = list()

                recipe_rows = recipe_html.find_elements(By.XPATH, './tbody/tr')
                for row in recipe_rows:
                    if not row.find_elements(By.XPATH, ".//td[contains(text(), 'Total')]"):
                        if row.find_elements(By.CSS_SELECTOR, "svg[viewBox*='0 0']"):
                            recipe_colourants.append(row.text.split('\n'))
                        else:
                            recipe_base.append(row.text.split('\n'))

                pa_Dict, umf_Dict = parse_umf_tables()

                glazy_entry = {
                    "Id": index,
                    "Subtype": glaze_subtype,
                    "Creation": created_metadata,
                    "OrtonCone": orton_cone,
                    "Atmosphere": atmospheres,
                    "Surface": surface,
                    "Transparency": transparency,
                    "Country": country,
                    "Description": description,
                    "Reviews": reviews,
                    "RecipeBase": recipe_base,
                    "Colorants": recipe_colourants,
                    "PercentAnalysis": pa_Dict,
                    "UMFAnalysis": umf_Dict,
                    "ImageTotal": imageCount,
                    "ImageDict": image_dict
                }

                glazy_list.append(glazy_entry)
                #add entry index from original df to drop list
                indices_to_drop.append(index)
                
        except WebDriverException as e:
            print(f"An error occurred: {e}")  # Print the error message
            input("press any key...")

        finally:
            #add current df to pickle
            #save dictionary into pkl file with date
            df = pd.DataFrame(glazy_list)

            dt = datetime.now().strftime("%Y%m%d_%H%M%S")

            df.to_pickle(f'glazy_data_{dt}.pkl')

            print(f"\nDataFrame saved to 'glazy_data_{dt}.pkl'")
            #drop id's that have been processed and update pickle
            print(f'processed {len(indices_to_drop)} out of {id_df.size}')

            cleaned_df = id_df.drop(indices_to_drop)
            dt = datetime.now().strftime("%Y%m%d_%H%M%S")
            cleaned_df.to_pickle('remaining_glazy_ids.pkl') #f'remaining_glazy_ids_{dt}.pkl')
            print(f'removed: {indices_to_drop}')

        # Load the DataFrame from the pickle file
        #loaded_df = pd.read_pickle(f'glazy_id_lists_top_production_{dt}.pkl')
        #print(loaded_df)

        """
        Lost ids:
        removed: ['536548', '536557', '536540', '148301', '523700', '502968', '22425', '16950', '3235', '148329', '58654', '3211', '6066', '1458', '29008', '29840', '90638', '65934', '26388', '407952', '531534', '7042', '32750', '164267', '78227', '145832', '459703', '18769', '6955', '524225', '6965', '16989', '16544', '519249', '500438', '361666', '452860', '21383', '30735', '378993', '426108', '270521', '507211', '2376', '49554', '21743', '21341', '519056', '3395', '7312', '2370', '362296', '38152', '26390', '36746', '452775', '21365', '7968', '127414', '425012']
        """

    except Exception as e:
        print(e)
        DRIVER.close()
    

if __name__ == "__main__":
    main()
