import requests
import xlwt
from xlwt import Workbook
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

BASE_URL = 'https://remoteok.com/api/'

# user agent value to tell webserve what kind of user is accessing the data (mobile/webbrowser/device...)
# get your own user agent info from whatismybrowser.com 
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.114 Safari/537.36'
REQUEST_HEADER = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US, en;q=0.5',
}

def get_job_postings():
    res = requests.get(url=BASE_URL,
                       headers=REQUEST_HEADER,
                       verify=False)
    return res.json()

def output_jobs_to_xls(data):
    #takes the json data of all the jobs 
    # go through data and get its keys and values 

    wb = Workbook()
    job_sheet = wb.add_sheet('Jobs')

    #get headers of one entry and add them to xls
    headers = list(data[0].keys())
    print(headers)
    for i in range(0,len(headers)):
        #put headers in xcl file
        job_sheet.write(0,i,headers[i])

    for i in range(0,len(data)):
        # add data for each job entry
        job = data[i]
        values = list(job.values())
        for x in range(0, len(values)):
            # skip the header rows, and for each entry fill in the values of its x column
            job_sheet.write(i+1, x, values[x])
    wb.save('remote_jobs.xls')

if __name__ == "__main__":
    json = get_job_postings()[1:]
    output_jobs_to_xls(json)