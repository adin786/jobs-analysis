import IndeedScraper as ind

# ind.batch_scrape([('Data Scientist', 'Scotland'),
#                   ('Data Engineer', 'Scotland'),
#                   ('Data Analyst', 'Scotland'),
#                   ('Business Analyst', 'Scotland'),
#                   ('Machine Learning Engineer', 'Scotland'),
#                   ('Machine Learning', 'Scotland'),
#                   ('Artificial Intelligence', 'Scotland'),
#                   ('AI', 'Scotland'),
#                   ('Data', 'Scotland')],
#                  pages=20,
#                  delay=5,
#                  append=False)

ind.batch_scrape([('Data Scientist', 'England'),
                  ('Data Engineer', 'England'),
                  ('Data Analyst', 'England'),
                  ('Business Analyst', 'England'),
                  ('Machine Learning Engineer', 'England'),
                  ('Machine Learning', 'England'),
                  ('Artificial Intelligence', 'England'),
                  ('AI', 'England'),
                  ('Data', 'England')],
                 pages=20,
                 delay=5,
                 f_name='data_england.csv',
                 append=False)
