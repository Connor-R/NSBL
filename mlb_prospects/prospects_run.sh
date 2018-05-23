SHELL=/bin/bash
source "/Users/connordog/.bash_profile"

python mlb_prospect_scraper.py --end_year 2018 --scrape_length "All"

wait

python mlb_prospect_grades.py

wait

python fangraphs_prospect_scraper.py --end_year 2018 --scrape_length "All"

wait