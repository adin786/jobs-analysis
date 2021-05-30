import requests
from bs4 import BeautifulSoup
import pandas as pd

def extract(url):    
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    jobs = soup.find_all(class_='react-job-listing')
    i=1
    for i, job in enumerate(jobs):
        if i>0: break
        
        job_title = job.get('data-normalize-job-title')
        
        joblink = job.find(class_='jobLink')
        job_url = f'{base_url}{joblink.get("href")}'
        

        print(f'Job:{job_title}\n{job_url}')   
        print(job.div)
 
    
    return

base_url = 'https://www.glassdoor.co.uk'
search_url = 'https://www.glassdoor.co.uk/Job/glasgow-data-scientist-jobs-SRCH_IL.0,7_IC3298888_KO8,22.htm'


extract(search_url)
