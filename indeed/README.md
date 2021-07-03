# IndeerScraper

A webscraper class  for extracting job advert data from (uk.indeed.com)

Requirements
```
pandas
requests
BeautifulSoup4
```

# Usage
Create an instance of the IndeedScraper.SearchScraper class with a job title and location as the query inputs
> import IndeedScraper as ind
> scraper = ind.SearchScraper(title='Data Scientist', loc='Scotland')

Run the scraping routine on first 3 pages.  This extracts the searchpage listings which contain everything except the actual job description text.
> scraper.scrape(pages=3)

To get the job description text, run the following line.  This is a time consuming step as it puts a separate server request for each job ad.
> scraper.add_descriptions()

And optionally
> scraper.drop_duplicates()

All scraped data can be accessed in a single PandasDataframe object stored inside the class
> scraper.df.head()

Alternatively, I've provided a helper function that batch scrapes a series of queries if input as a list of tuples.  For each query in the list, a new instance of the scraper class is created, scraped, then output is written to or appended to a .csv file (in case something fails in the middle of the scrape)
> ind.batch_scrape([('Data Scientist', 'Scotland'),
                  ('Data Engineer', 'Scotland'),
                  ('Data Analyst', 'Scotland')])
                  
I've been able to scrape about 500 or so jobs (with a 5 second constant sleep added between server request), before I started receiving a rate limiting page.  Perhaps could consider running with a longer, or slightly more randomised delay.