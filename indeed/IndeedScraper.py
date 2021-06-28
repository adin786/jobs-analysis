import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_url_page(url_start, page):
    if page==0:
        return url_start
    else:
        url_page = f'{url_start}&start={page*10}'
        return url_page
    
    
def get_title(title):
    if isinstance(title,str):
        title = title.lower().strip().replace(' ','+')
    else:
        raise Exception('title must be str type')
    return title


def get_job_search(url, base_url, headers, verbose=True):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extract list of jobcards
    jobs_list = soup.find(id='resultsCol')
    jobcards = soup.find_all(class_='jobsearch-SerpJobCard')

    # Loop through each job result listed on page
    df_page = pd.DataFrame()
    for j, card in enumerate(jobcards):
        # if j > 1: break

        card_title = card.find(class_='jobtitle')
        card_title_str = card_title.text.strip()
        card_url = base_url + card_title['href']

        card_id = card['id']

        card_company = card.find('span', class_='company')
        card_company = card_company.text.strip()

        card_loc = card.find(class_='location')
        card_loc_str = card_loc.text.strip()

        card_summary = card.find(class_='summary')
        card_summary_str = card_summary.text.strip()

        card_date = card.find(class_='date')
        card_date_str = card_date.text.strip()

        if verbose: print(f'job:{j:2} title:{card_title_str[:20]:20} company:{card_company}')

        df_page = df_page.append({
            'title': card_title_str,
            'id': card_id,
            'company': card_company,
            'url': card_url,
            'location': card_loc_str,
            'summary': card_summary_str,
            'date': card_date_str
        }, ignore_index=True)
        
        
    if df_page.empty:
        print(jobs_list.prettify())
    return df_page

def get_job_description(url, headers):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    description_html = soup.find(id='jobDescriptionText')
    description_str = description_html.text.strip()
    
    descr = {'description':description_str,
             'description_html':description_html}         
    return descr


class SearchPageScraper:
    base_url = 'https://uk.indeed.com'
    base_url_jobs = '/jobs?'
    
    def __init__(self, title, loc):
        self.title = get_title(title)
        self.loc = loc
        self.df = pd.DataFrame(columns=['title','id','company','url','location','summary',
                                        'date', 'description', 'description_html'])
        self.url = f'{self.base_url}{self.base_url_jobs}q={self.title}&l={self.loc}'
        self.headers = {'Uer-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
        self.pages_scraped = 0
        self.descriptions_scraped = 0
        
    def new_search(self, title, loc):
        self.title = get_title(title)
        self.loc = loc
        self.url = f'{self.base_url}{self.base_url_jobs}q={self.title}&l={self.loc}'

    def pre_check(self):
        print('Input validation not written yet')
    
    def __repr__(self):
        if self.df.empty:
            repr = (f'IndeedScraper(title="{self.title}", loc="{self.loc}")\n'
                    f'  - Empty df, no results loaded')
        else:
            repr = (f'IndeedScraper(title="{self.title}", loc="{self.loc}")\n'
                    f'  - {len(self.df)} jobs scraped from {self.pages_scraped} pages')
        return repr
        
    def scrape(self, num_pages=1, attempts=3, verbose=True):
        print(f'Running scraper for [{self.title}] in [{self.loc}]')
        
        for i in range(0, num_pages):
            # if i>0: break

            # Retry if blank result
            for attempt in range(attempts):
                url_page = get_url_page(self.url, i)
                if verbose: print(f'\nPage:{i} url:{url_page}')

                # Request page
                time.sleep(1)
                df_page = get_job_search(url_page, self.base_url, self.headers, verbose=True)

                if df_page.empty:
                    if verbose: print(f'Blank result, retrying ({attempt+1} of {attempts} attempts)')
                    time.sleep(1)
                    continue
                else:
                    self.df = self.df.append(df_page, ignore_index=True)
                    break
            self.pages_scraped = self.pages_scraped + 1
    
    
    def new_query(self, title, loc):
        self.title = get_title(title)
        self.loc = loc
        self.url = f'{self.base_url}{self.base_url_jobs}q={self.title}&l={self.loc}'
        
        
    def drop_duplicates(self):
        print(f'{len(self.df)} rows before dropping duplicates')
        self.df = self.df.drop_duplicates('id')
        print(f'{len(self.df)} rows after dropping duplicates')
        

    def add_descriptions(self):
        if self.df.empty:
            raise Exception('No existing scraped data.  First use .scrape() method')
        
        for i, row in self.df.iterrows():                        
            if not pd.isna(row.description):
                print(f'row {i:2}, description already added, skipping')
                continue
            else:
                time.sleep(1)
                descr_dict = get_job_description(row.url, self.headers)
                print(f'row {i:2}, description added ({len(descr_dict)} characters)')
                
                row.description = descr_dict['description']
                row.description_html = descr_dict['description_html']
                self.descriptions_scraped = self.descriptions_scraped+1
            