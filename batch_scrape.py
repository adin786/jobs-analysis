import indeed.IndeedScraper as ind

ind.batch_scrape([('Data Scientist', 'Scotland'),
                  ('Data Engineer', 'Scotland'),
                  ('Data Analyst', 'Scotland'),
                  ('Business Analyst', 'Scotland'),
                  ('Machine Learning Engineer', 'Scotland'),
                  ('Machine Learning', 'Scotland'),
                  ('Artificial Intelligence', 'Scotland'),
                  ('AI', 'Scotland'),
                  ('Data', 'Scotland')],
                 pages=20,
                 delay=5,
                 append=False)
