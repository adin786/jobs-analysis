import logging
from .scraping import SearchPageScraper
import os

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def batch_scrape(
    queries: list, 
    pages: int = 5,
    delay: int = 5,
    append: bool = False,
    f_name: str = "data.csv",
    verbose: bool = False,
):
    for i, query in enumerate(queries):
        print(f'Looping through query: "{query[0]}" in "{query[1]}"')
        logger.info(f'Looping through query: "{query[0]}" in "{query[1]}"')

        scraper = SearchPageScraper(query[0], query[1], delay=delay)
        scraper.scrape(pages, verbose=verbose)

        scraper.add_descriptions()
        scraper.drop_duplicates()

        if i == 0 and not append:
            if not os.path.isdir("data"):
                os.mkdir("data")
            scraper.save(os.path.join("data", f_name), append=False)
        else:
            scraper.save(os.path.join("data", f_name), append=True)
    return