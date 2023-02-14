import os
import re
import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_url_page(url_start, page):
    if page == 0:
        return url_start
    else:
        url_page = f"{url_start}&start={page*10}"
        return url_page


def get_title(title):
    if isinstance(title, str):
        title = title.lower().strip().replace(" ", "+")
    else:
        raise ValueError("title must be str type")
    return title


def get_job_search(url, base_url, headers, verbose=True):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    # Extract list of jobcards
    jobcards = soup.find_all(class_="jobsearch-SerpJobCard")
    df_page = pd.DataFrame()

    if len(jobcards) > 0:
        # Loop through each job result listed on page
        for i, card in enumerate(jobcards):
            # if j > 1: break

            card_title = card.find(class_="jobtitle")
            card_title_str = card_title.text.strip()
            card_url = base_url + card_title["href"]

            card_id = card["id"]
            # card_id = re.sub(r'job_|sj_|p_|pj_','',card_id)
            card_id = re.sub(r".*_", "", card_id)

            card_company = card.find("span", class_="company")
            card_company_str = card_company.text.strip()

            card_loc = card.find(class_="location")
            card_loc_str = card_loc.text.strip()

            card_salary = card.find(class_="salary-snippet")
            card_salary_str = (
                card_salary.text.strip() if card_salary is not None else ""
            )

            card_summary = card.find(class_="summary")
            card_summary_str = card_summary.text.strip()

            card_date = card.find(class_="date")
            card_date_str = card_date.text.strip()

            card_title_short = (
                card_title_str[0:20] if len(card_title_str) > 20 else card_title_str
            )
            if verbose:
                print(
                    f"job:{i:2} title:{card_title_short:<20}... company:{card_company_str}"
                )
            logger.debug(
                f"job:{i:2} title:{card_title_short:<20}... company:{card_company_str}"
            )

            df_page = df_page.append(
                {
                    "title": card_title_str,
                    "id": card_id,
                    "company": card_company_str,
                    "url": card_url,
                    "salary": card_salary_str,
                    "location": card_loc_str,
                    "summary": card_summary_str,
                    "date": card_date_str,
                    "page_format": 0,
                },
                ignore_index=True,
            )
    else:
        # Use this routine if the alternative page format is received.
        # Haven't worked out why there are 2 formats yet, works either way
        jobcards = soup.find_all(class_="tapItem")

        for i, card in enumerate(jobcards):
            card_url = base_url + card["href"]

            card_title = card.find(class_="jobTitle")
            card_title_str = card_title.text.strip()

            card_id = card["id"]
            # card_id = re.sub(r'job_|sj_|p_|pj_','',card_id)
            card_id = re.sub(r".*_", "", card_id)

            card_company = card.find(class_="companyName")
            card_company_str = card_company.text.strip()

            card_loc = card.find(class_="companyLocation")
            card_loc_str = card_loc.text.strip()

            card_salary = card.find(class_="salary-snippet")
            card_salary_str = (
                card_salary.text.strip() if card_salary is not None else ""
            )

            card_summary = card.find(class_="job-snippet")
            card_summary_str = card_summary.text.strip()

            card_date = card.find(class_="date")
            card_date_str = card_date.text.strip()

            card_title_short = (
                card_title_str[0:20] if len(card_title_str) > 20 else card_title_str
            )
            if verbose:
                print(
                    f"job:{i:2} title:{card_title_short:<20}... company:{card_company_str}"
                )
            logger.debug(
                f"job:{i:2} title:{card_title_short:<20}... company:{card_company_str}"
            )

            df_page = df_page.append(
                {
                    "title": card_title_str,
                    "id": card_id,
                    "company": card_company_str,
                    "url": card_url,
                    "salary": card_salary_str,
                    "location": card_loc_str,
                    "summary": card_summary_str,
                    "date": card_date_str,
                    "page_format": 1,
                },
                ignore_index=True,
            )

        # output file for debugging
        # html = soup.prettify("utf-8")
        # with open('failedpage.html', 'wb') as file:
        #     file.write(html)
    return df_page


def get_job_description(url, headers):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    description_html = soup.find(id="jobDescriptionText")
    description_str = description_html.text.strip()

    descr = {"description": description_str, "description_html": str(description_html)}
    return descr
