import requests
import datetime
import os.path
from bs4 import BeautifulSoup

url = "https://finance.yahoo.com/quote/AAPL/?p=AAPL"
url = "https://www.glazespectrum.com/"

prop = "Previous Close"

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.114 Safari/537.36'
REQUEST_HEADER = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US, en;q=0.5',
}


if __name__ == "__main__":

    response = requests.get(url,
                            verify=False,
                            headers=REQUEST_HEADER)

    soup = BeautifulSoup(response.text, features="html.parser")

    #find elements of some type
    li = soup.find_all("li")
    # access their text by .text for each element returned

    #You can also access the first element of its subelements with their element names
    li[0].span.text

    #use .content to get all the subelements of an element
    li[0].contents[1].text

    #use find all to search based on specific class names
    ul = soup.find_all("ul", class_="yf-1jj98ts")
    #print(ul[0].li.text)

    ul = soup.find_all('ul')
    #you can search by attribute in a soup
    print(ul[0].find("fin-streamer",attrs={"data-field":"regularMarketPreviousClose"}))

    #use contents to access all the subelements
    print(ul[0].contents[1].text)

    datetime.datetime.now().timestamp()

    os.path.isfile('name') # does a file exist
