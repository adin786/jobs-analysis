import indeed.IndeedScraper as ind

scraper = ind.SearchPageScraper('Data Scientist', 'Scotland')

scraper.scrape(2, verbose=True)

# Debugging the blank pages