import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import logging

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log')

# Create formatters and add it to handlers
c_handler.setFormatter(logging.Formatter('[%(levelname)s]%(message)s'))
f_handler.setFormatter(logging.Formatter('[%(asctime)s:%(name)s:%(levelname)s]%(message)s'))

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)
logger.setLevel(logging.DEBUG)


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
    jobcards = soup.find_all(class_='jobsearch-SerpJobCard')
    df_page = pd.DataFrame()

    if len(jobcards) > 0:
        # Loop through each job result listed on page
        for i, card in enumerate(jobcards):
            # if j > 1: break

            card_title = card.find(class_='jobtitle')
            card_title_str = card_title.text.strip()
            card_url = base_url + card_title['href']

            card_id = card['id']
            # card_id = re.sub(r'job_|sj_|p_|pj_','',card_id)
            card_id = re.sub(r'.*_','',card_id)

            card_company = card.find('span', class_='company')
            card_company_str = card_company.text.strip()

            card_loc = card.find(class_='location')
            card_loc_str = card_loc.text.strip()

            card_salary = card.find(class_='salary-snippet')
            card_salary_str = card_salary.text.strip() if card_salary is not None else ''

            card_summary = card.find(class_='summary')
            card_summary_str = card_summary.text.strip()

            card_date = card.find(class_='date')
            card_date_str = card_date.text.strip()
               
            card_title_short = card_title_str[0:20] if len(card_title_str)>20 else card_title_str
            if verbose: print(f'job:{i:2} title:{card_title_short:<20}... company:{card_company_str}')
            logger.debug(f'job:{i:2} title:{card_title_short:<20}... company:{card_company_str}')

            df_page = df_page.append({
                'title': card_title_str,
                'id': card_id,
                'company': card_company_str,
                'url': card_url,
                'salary': card_salary_str,
                'location': card_loc_str,
                'summary': card_summary_str,
                'date': card_date_str,
                'page_format': 0
            }, ignore_index=True)
    else:
        # Use this routine if the alternative page format is received.  
        # Haven't worked out why there are 2 formats yet, works either way
        jobcards = soup.find_all(class_='tapItem')
        
        for i, card in enumerate(jobcards):
            card_url = base_url + card['href']
            
            card_title = card.find(class_='jobTitle')
            card_title_str = card_title.text.strip()
            
            card_id = card['id']
            # card_id = re.sub(r'job_|sj_|p_|pj_','',card_id)
            card_id = re.sub(r'.*_','',card_id)

            card_company = card.find(class_='companyName')
            card_company_str = card_company.text.strip()
            
            card_loc = card.find(class_='companyLocation')
            card_loc_str = card_loc.text.strip()
            
            card_salary = card.find(class_='salary-snippet')
            card_salary_str = card_salary.text.strip() if card_salary is not None else ''
            
            card_summary = card.find(class_='job-snippet')
            card_summary_str = card_summary.text.strip()
            
            card_date = card.find(class_='date')
            card_date_str = card_date.text.strip()
            
            card_title_short = card_title_str[0:20] if len(card_title_str)>20 else card_title_str
            if verbose: print(f'job:{i:2} title:{card_title_short:<20}... company:{card_company_str}')
            logger.debug(f'job:{i:2} title:{card_title_short:<20}... company:{card_company_str}')
            
            df_page = df_page.append({
                'title': card_title_str,
                'id': card_id,
                'company': card_company_str,
                'url': card_url,
                'salary': card_salary_str,
                'location': card_loc_str,
                'summary': card_summary_str,
                'date': card_date_str,
                'page_format':1
            }, ignore_index=True)
            
        # output file for debugging
        # html = soup.prettify("utf-8")
        # with open('failedpage.html', 'wb') as file:
        #     file.write(html)
    return df_page

def get_job_description(url, headers):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    description_html = soup.find(id='jobDescriptionText')
    description_str = description_html.text.strip()
    
    descr = {'description':description_str,
             'description_html':str(description_html)}         
    return descr

def batch_scrape(queries, pages=5, delay=5, append=False, verbose=False):
    for i, query in enumerate(queries):
        print(f'Looping through query: "{query[0]}" in "{query[1]}"')
        logger.info(f'Looping through query: "{query[0]}" in "{query[1]}"')
        
        scraper = SearchPageScraper(query[0], query[1], delay=delay)
        scraper.scrape(pages, verbose=verbose)

        scraper.add_descriptions()    
        scraper.drop_duplicates()
        
        if i == 0 and not append:
            scraper.save('data.csv', append=False)
        else:
            scraper.save('data.csv', append=True)
    return


class SearchPageScraper:
    base_url = 'https://uk.indeed.com'
    base_url_jobs = '/jobs?'
    
    def __init__(self, title, loc, delay=1):
        self.title = get_title(title)
        self.loc = loc
        self.df = pd.DataFrame(columns=['title','id','company','url','location','summary',
                                        'date', 'description', 'description_html'])
        self.url = f'{self.base_url}{self.base_url_jobs}q={self.title}&l={self.loc}'
        self.headers = {'Uer-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
        self.pages_scraped = 0
        self.descriptions_scraped = 0
        self.delay = delay
        
    def new_search(self, title, loc):
        self.title = get_title(title)
        self.loc = loc
        self.url = f'{self.base_url}{self.base_url_jobs}q={self.title}&l={self.loc}'

    def pre_check(self):
        print('Input validation not written yet')
        logger.debug('Input validation not written yet')
    
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
        logger.info(f'Running scraper for [{self.title}] in [{self.loc}]')
        
        for i in range(0, num_pages):
            # if i>0: break

            # Retry if blank result
            attempt_success = False
            retrying = ''
            for attempt in range(attempts):
                url_page = get_url_page(self.url, i)
                
                if retrying == '':
                    print(f'\nPage:{i+1} url:{url_page}')
                    logger.info(f'Scraping page:{i+1} url:{url_page}')
                else:
                    print(retrying)
                    logger.info(retrying)
                
                # Request page
                time.sleep(self.delay)
                try:
                    df_page = get_job_search(url_page, self.base_url, self.headers, verbose=verbose)
                except:
                    df_page = pd.DataFrame()
                    logger.warning('Failed to scrape this page')

                if df_page.empty:
                    retrying = f'Blank result, retrying ({attempt+1} of {attempts} attempts)'
                    continue
                else:
                    attempt_success = True
                    df_page['query_title'] = self.title
                    df_page['query_loc'] = self.loc
                    break
            
            if attempt_success:
                self.pages_scraped = self.pages_scraped + 1
                this_id_list = df_page.id.values.tolist()
                id_duplicates = [any(self.df.id.str.contains(x)) for x in this_id_list]
                # if verbose: print(id_duplicates)
                
                self.df = self.df.append(df_page, ignore_index=True)
                
                if all(id_duplicates):
                    print(f'Stopping scraper as this page found {sum(id_duplicates)} duplicates (of {len(id_duplicates)} on this page)')
                    logger.info(f'Stopping scraper as this page found {sum(id_duplicates)} duplicates (of {len(id_duplicates)} on this page)')
                    break   
        logger.info(f'{len(self.df)} entries scraped from {i} pages (out of {num_pages})') 
    
    def new_query(self, title, loc):
        self.title = get_title(title)
        self.loc = loc
        self.url = f'{self.base_url}{self.base_url_jobs}q={self.title}&l={self.loc}'
        
    def drop_duplicates(self):
        print(f'{len(self.df)} rows before dropping duplicates')
        logger.info(f'{len(self.df)} rows before dropping duplicates')
        self.df = self.df.drop_duplicates('id')
        self.df = self.df.reset_index(drop=True)
        print(f'{len(self.df)} rows after dropping duplicates')
        logger.info(f'{len(self.df)} rows after dropping duplicates')
        
    def add_descriptions(self, verbose=False):
        if self.df.empty:
            raise Exception('No existing scraped data.  First use .scrape() method')
        
        for i, row in self.df.iterrows():   
            comp_name = row.company[:10] if len(row.company)>10 else row.company
            if not pd.isna(row.description):
                if verbose: print(f'desc:{i:2} {comp_name:<10}... description already added, skipping')
                logger.info(f'desc:{i:2} {comp_name:<10}... description already added, skipping')
                continue
            else:
                time.sleep(self.delay)
                descr_dict = get_job_description(row.url, self.headers)
                if verbose: print(f'desc:{i:2} {comp_name:<10}... description added ({len(descr_dict["description"])} characters)')
                logger.info(f'desc:{i:2} {comp_name:<10}... description added ({len(descr_dict["description"])} characters)')
                
                self.df.iloc[self.df.index[i], self.df.columns.get_loc('description')] = descr_dict['description']
                self.df.iloc[self.df.index[i], self.df.columns.get_loc('description_html')] = descr_dict['description_html']
                
                self.descriptions_scraped = self.descriptions_scraped+1
                
    def save(self, f_name, append=False):
        if append:
            self.df.to_csv(f_name, index=True, mode='a', header=False)
            print(f'Data appended to {f_name}')
            logger.info(f'Data appended to {f_name}')
        else:
            self.df.to_csv(f_name, index=True, mode='w', header=True)
            print(f'Data saved to {f_name}')
            logger.info(f'Data saved to {f_name}')

        
            