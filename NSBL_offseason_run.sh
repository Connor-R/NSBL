#!/bin/sh
# Shell script to run after each weekly sim (updates registers, statistics, and historical statistics)
# Remember to first download the new rosters/zip file before running

SHELL=/bin/bash
source "/Users/connordog/.bash_profile"

year=2021
date=$( date +"%b %d, %Y" )


echo starting offseason run
echo $(date)

wait

cd processing
python NSBL_excel_rosters_GoogleSheets.py
cd ..


wait

python processing/NSBL_historical_stats.py

wait

python processing/NSBL_Draft_FA_HOF.py --year "$year"

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

echo offseason run completed