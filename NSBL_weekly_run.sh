# Shell script to run after each weekly sim (updates registers, statistics, and historical statistics)
# Remember to first download the new rosters/zip file before running

SHELL=/bin/bash
source "/Users/connordog/.bash_profile"

python scrapers/NSBL_register_scraper.py
python scrapers/NSBL_scraper.py

wait

python processing/NSBL_current_rosters_excel.py

wait

python processing/NSBL_processed_league_averages.py
python processing/NSBL_processed_compWAR_defensive.py

wait

python processing/NSBL_processed_compWAR_offensive.py
python processing/NSBL_processed_WAR_pitchers.py

wait

python processing/NSBL_processed_WAR_hitters.py

wait

python processing/NSBL_processed_WAR_team.py
python processing/NSBL_historical_stats_primary.py
python processing/NSBL_historical_stats_advanced.py

wait

python processing/NSBL_processed_team_standings_advanced.py

wait

python processing/NSBL_processed_team_hitting.py
python processing/NSBL_processed_team_defense.py
python processing/NSBL_processed_team_pitching.py

wait

python team_strength/lineup_optimizer.py
python team_strength/pitching_optimizer.py

wait

python team_strength/team_strength.py

wait

python team_strength/playoff_probabilities.py