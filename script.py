import indeed.IndeedScraper as ind

scraper = ind.SearchPageScraper('Data Scientist', 'Scotland')

scraper.scrape(1, attempts=2, verbose=True)
