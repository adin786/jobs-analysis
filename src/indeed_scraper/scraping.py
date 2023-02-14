import logging
import time
import pandas as pd
from .utils import get_job_description, get_title, get_job_search, get_url_page



# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SearchPageScraper:
    base_url = "https://uk.indeed.com"
    base_url_jobs = "/jobs?"

    def __init__(self, title, loc, delay=1):
        self.title = get_title(title)
        self.loc = loc
        self.df = pd.DataFrame(
            columns=[
                "title",
                "id",
                "company",
                "url",
                "location",
                "summary",
                "date",
                "description",
                "description_html",
            ]
        )
        self.url = f"{self.base_url}{self.base_url_jobs}q={self.title}&l={self.loc}"
        self.headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        self.pages_scraped = 0
        self.descriptions_scraped = 0
        self.delay = delay

    def new_search(self, title, loc):
        self.title = get_title(title)
        self.loc = loc
        self.url = f"{self.base_url}{self.base_url_jobs}q={self.title}&l={self.loc}"

    def pre_check(self):
        print("Input validation not written yet")
        logger.debug("Input validation not written yet")

    def __repr__(self):
        if self.df.empty:
            repr = (
                f'IndeedScraper(title="{self.title}", loc="{self.loc}")\n'
                f"  - Empty df, no results loaded"
            )
        else:
            repr = (
                f'IndeedScraper(title="{self.title}", loc="{self.loc}")\n'
                f"  - {len(self.df)} jobs scraped from {self.pages_scraped} pages"
            )
        return repr

    def scrape(self, num_pages=1, attempts=3, verbose=True):
        logger.info(f"Running scraper for [{self.title}] in [{self.loc}]")

        for i in range(0, num_pages):
            # if i>0: break

            # Retry if blank result
            attempt_success = False
            retrying = ""
            for attempt in range(attempts):
                url_page = get_url_page(self.url, i)

                if retrying == "":
                    logger.info(f"Scraping page:{i+1} url:{url_page}")
                else:
                    logger.info(retrying)

                # Request page
                time.sleep(self.delay)
                try:
                    df_page = get_job_search(
                        url_page, self.base_url, self.headers, verbose=verbose
                    )
                except:
                    df_page = pd.DataFrame()
                    logger.warning("Failed to scrape this page")

                if df_page.empty:
                    retrying = (
                        f"Blank result, retrying ({attempt+1} of {attempts} attempts)"
                    )
                    continue
                else:
                    attempt_success = True
                    df_page["query_title"] = self.title
                    df_page["query_loc"] = self.loc
                    break

            if attempt_success:
                self.pages_scraped = self.pages_scraped + 1
                this_id_list = df_page.id.values.tolist()
                id_duplicates = [any(self.df.id.str.contains(x)) for x in this_id_list]
                # if verbose: print(id_duplicates)

                self.df = self.df.append(df_page, ignore_index=True)

                if all(id_duplicates):
                    print(
                        f"Stopping scraper as this page found {sum(id_duplicates)} duplicates (of {len(id_duplicates)} on this page)"
                    )
                    logger.info(
                        f"Stopping scraper as this page found {sum(id_duplicates)} duplicates (of {len(id_duplicates)} on this page)"
                    )
                    break
        logger.info(
            f"{len(self.df)} entries scraped from {i} pages (out of {num_pages})"
        )

    def new_query(self, title, loc):
        self.title = get_title(title)
        self.loc = loc
        self.url = f"{self.base_url}{self.base_url_jobs}q={self.title}&l={self.loc}"

    def drop_duplicates(self):
        print(f"{len(self.df)} rows before dropping duplicates")
        logger.info(f"{len(self.df)} rows before dropping duplicates")
        self.df = self.df.drop_duplicates("id")
        self.df = self.df.reset_index(drop=True)
        print(f"{len(self.df)} rows after dropping duplicates")
        logger.info(f"{len(self.df)} rows after dropping duplicates")

    def add_descriptions(self, verbose=False):
        if self.df.empty:
            raise Exception("No existing scraped data.  First use .scrape() method")

        for i, row in self.df.iterrows():
            comp_name = row.company[:10] if len(row.company) > 10 else row.company
            if not pd.isna(row.description):
                if verbose:
                    print(
                        f"desc:{i:2} {comp_name:<10}... description already added, skipping"
                    )
                logger.info(
                    f"desc:{i:2} {comp_name:<10}... description already added, skipping"
                )
                continue
            else:
                time.sleep(self.delay)
                try:
                    descr_dict = get_job_description(row.url, self.headers)
                    if verbose:
                        print(
                            f'desc:{i:2} {comp_name:<10}... description added ({len(descr_dict["description"])} characters)'
                        )
                    logger.info(
                        f'desc:{i:2} {comp_name:<10}... description added ({len(descr_dict["description"])} characters)'
                    )
                except:
                    descr = {"description": "", "description_html": ""}
                    logger.info(
                        f'desc:{i:2} {comp_name:<10}... FAILED to read description ({len(descr_dict["description"])} characters)'
                    )

                self.df.iloc[
                    self.df.index[i], self.df.columns.get_loc("description")
                ] = descr_dict["description"]
                self.df.iloc[
                    self.df.index[i], self.df.columns.get_loc("description_html")
                ] = descr_dict["description_html"]

                self.descriptions_scraped = self.descriptions_scraped + 1

    def save(self, f_name, append=False):
        if append:
            self.df.to_csv(f_name, index=True, mode="a", header=False)
            print(f"Data appended to {f_name}")
            logger.info(f"Data appended to {f_name}")
        else:
            self.df.to_csv(f_name, index=True, mode="w", header=True)
            print(f"Data saved to {f_name}")
            logger.info(f"Data saved to {f_name}")
