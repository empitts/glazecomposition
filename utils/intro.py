import requests

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
    print(response)
    print(response.status_code == 200)

    t = response.text
    ind = t.index("Previous Close")
    print(ind)

    #each time it finds the </span it will separate the text into list of those chuncks
    redText = t[ind:].split("</span>")

    """
    Example list after spli:
    ['Previous Close">Previous Close', 
    ' <span class="value yf-1jj98ts"><fin-streamer data-symbol="AAPL" data-value="201.00" data-trend="none" active data-field="regularMarketPreviousClose" class="yf-1jj98ts">201.00 </fin-streamer>', 
    ' </li>   <li class="yf-1jj98ts"><span class="label yf-1jj98ts" title="Open">Open']
    """
    # value we want is in the second list entry: 201.00 or so
    redText = redText[1]
    print(redText)

    val = redText.split(">")[-1]
    
    print(val)
