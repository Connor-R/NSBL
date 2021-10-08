SHELL=/bin/bash
source "/Users/connordog/.bash_profile"

updateDate=$( date +"%b %d, %Y" )
year=2021

python weekly_projection_charts.py --year "$year"

wait

python export_leaderboards.py --year "$year"

wait

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_leaderboard_Standings.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/leaderboard_Standings.html -c "NSBL $year - Advanced Standings (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/leaderboard_Standings.html"

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_leaderboard_Changes.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/leaderboard_Changes.html -c "NSBL $year - Weekly Changes (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/leaderboard_Changes.html"
wait

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_current_rosters.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/current_rosters.html -c "NSBL - Current Rosters (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/current_rosters.html"

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_current_team_summary.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/current_team_summary.html -c "NSBL - Current Team Summary (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/current_team_summary.html"


csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_historical_DraftPicks.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_DraftPicks.html -c "NSBL - Historical Draft Picks (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_DraftPicks.html"

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_historical_FreeAgency.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_FreeAgency.html -c "NSBL - Historical Free Agency (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_FreeAgency.html"

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_hall_of_fame.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/hall_of_fame.html -c "NSBL - Hall of Fame (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/hall_of_fame.html"

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_historical_rosters.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_rosters.html -c "NSBL - Historical Rosters (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_rosters.html"

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_historical_TeamDraftTable.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_TeamDraftTable.html -c "NSBL - Historical Team Draft Table (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_TeamDraftTable.html"

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_historical_TeamFreeAgencyTable.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_TeamFreeAgencyTable.html -c "NSBL - Historical Team Free Agency Table (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_TeamFreeAgencyTable.html"

wait

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_historical_StatsHitters.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_StatsHitters.html -c "NSBL - Historical Stats (Hitters) (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_StatsHitters.html"

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_historical_StatsPitchers.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_StatsPitchers.html -c "NSBL - Historical Stats (Pitchers) (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/historical_StatsPitchers.html"

wait

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_milestones.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/NSBL_milestones.html -c "NSBL - Milestone Watch (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/NSBL_milestones.html"


wait

csvtotable HIDDEN_Teams.csv HIDDEN_Teams.html -c "NSBL $year - Teams(hidden) (Last Updated $updateDate)" -vs 15 -o

csvtotable HIDDEN_Projections.csv HIDDEN_Projections.html -c "NSBL $year - Projections(hidden) (Last Updated $updateDate)" -vs 15 -o

csvtotable HIDDEN_FreeAgentBatters.csv HIDDEN_FreeAgentBatters.html -c "NSBL $year - Free Agent Batters(hidden) (Last Updated $updateDate)" -vs 15 -o

csvtotable HIDDEN_FreeAgentPitchers.csv HIDDEN_FreeAgentPitchers.html -c "NSBL $year - Free Agent Pitchers(hidden) (Last Updated $updateDate)" -vs 15 -o

csvtotable HIDDEN_trade_value_players.csv HIDDEN_trade_value_players.html -c "NSBL $year - Trade Value Players(hidden) (Last Updated $updateDate)" -vs 15 -o

csvtotable HIDDEN_trade_value_teams.csv HIDDEN_trade_value_teams.html -c "NSBL $year - Trade Value Teams(hidden) (Last Updated $updateDate)" -vs 15 -o

wait

cd ~/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/
git add csvs/NSBL_*
git add Tables/*
git add i/NSBL_WeeklyProjections/*
git commit -m "weekly NSBL update ($updateDate)"
git push