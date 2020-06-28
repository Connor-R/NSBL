#!/bin/sh
# Shell script to run after each weekly sim (updates registers, statistics, and historical statistics)
# Remember to first download the new rosters/zip file before running

SHELL=/bin/bash
source "/Users/connordog/.bash_profile"

year=2015
date=$( date +"%b %d, %Y" )


echo starting weekly run
echo $(date)

python scrapers/NSBL_register_scraper.py --end_year "$year" --scrape_length "Current"
python scrapers/NSBL_scraper.py --end_year "$year" --scrape_length "Current"

wait

python processing/NSBL_processed_league_averages.py

wait

cd processing
python NSBL_excel_rosters_GoogleSheets.py
cd ..
# python processing/NSBL_excel_rosters.py --year "$year"

wait 

python processing/NSBL_processed_compWAR_defensive.py --year "$year"

wait

python processing/NSBL_processed_compWAR_offensive.py --year "$year"
python processing/NSBL_processed_WAR_pitchers.py --year "$year"

wait

python processing/NSBL_processed_WAR_hitters.py --year "$year"

wait

python processing/NSBL_processed_WAR_team.py --year "$year"
python processing/NSBL_historical_stats_primary.py
python processing/NSBL_historical_stats_advanced.py

wait

python processing/NSBL_processed_team_standings_advanced.py

wait

python processing/NSBL_processed_team_hitting.py
python processing/NSBL_processed_team_defense.py
python processing/NSBL_processed_team_pitching.py

wait

python team_strength/lineup_optimizer.py --year "$year"
python team_strength/pitching_optimizer.py --year "$year"

wait

python team_strength/team_strength.py --year "$year"

wait

python team_strength/playoff_probabilities.py --year "$year"

wait

python team_strength/trade_value.py --year "$year"

wait

python ad_hoc/zips_FA_contract_value.py

wait

python ad_hoc/zips_prep_FA.py --year "$year"

wait

cd weekly_leaderboards
bash post_leaderboards_run.sh

wait

echo weekly run completed
