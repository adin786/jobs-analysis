from indeed.IndeedScraper import SearchPageScraper
from indeed.IndeedScraper import JobPageScraper


# Create instance of class
scraper = SearchPageScraper('Data Scientist', 'Scotland')

# Print the object before
print(scraper)

# Run the scraper and print it
scraper.scrape(2, verbose=True)
print(scraper)

# Try the JobPageScraper
this_url = scraper.df['url'].iloc[0]
job_scraper = JobPageScraper(this_url)
print(job_scraper)

# # Update the search query, run the scraper and print it
# scraper.new_query('Data Analyst', 'Edinburgh')
# scraper.scrape(2, verbose=True)
# print(scraper)

# # Remove duplicates
# scraper.drop_duplicates()
# print(scraper)
