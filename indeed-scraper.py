import requests
from bs4 import BeautifulSoup
import pandas as pd

# Inputs
base_url = 'https://uk.indeed.com'
base_url_jobs = '/jobs?'
query_title = 'data+scientist'
query_loc = 'Scotland'

url_start = f'{base_url}{base_url_jobs}q={query_title}&l={query_loc}'
headers = {'Uer-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

# print(url_start)

def get_url_page(url_start, page):
    if page==0:
        return url_start
    else:
        url_page = f'{url_start}&start={page*10}'
        return url_page

df = pd.DataFrame()
i=0
for i in range(0,10):
    if i>0: break

    url_page = get_url_page(url_start, i)
    print(f'\nPage:{i} url:{url_page}')

    # Request page
    page = requests.get(url_page, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get list of jobcards
    jobs_list = soup.find(id='resultsCol')
    jobcards = soup.find_all(class_='jobsearch-SerpJobCard')

    page_empty = False
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

        # card_url = card.find

        print(f'job:{j:2} title:{card_title_str[:20]:20} company:{card_company}')

        df_page = df_page.append({
            'title': card_title_str,
            'id': card_id,
            'company': card_company,
            'url': card_url,
            'location': card_loc_str,
            'summary': card_summary_str,
            'date': card_date_str
        }, ignore_index=True)

    df = df.append(df_page, ignore_index=True)

# Drop duplicates before saving
# print('length before drop', len(df))
# df = df.drop_duplicates('id')
# print('length after drop', len(df))

print(df.T)
print(df.url.values)
