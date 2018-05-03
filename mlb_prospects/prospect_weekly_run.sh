SHELL=/bin/bash
source "/Users/connordog/.bash_profile"

python mlb_prospect_scraper.py

wait

python prospect_grades.py