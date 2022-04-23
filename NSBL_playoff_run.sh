SHELL=/bin/bash
source "/Users/connordog/.bash_profile"

updateDate=$( date +"%b %d, %Y" )
year=2021

python team_strength/in_playoff_probabilities.py --year "$year"

wait

cd weekly_leaderboards

python in_playoff_projection_charts.py --year "$year"

wait

python weekly_projection_charts.py --year "$year"

wait

python export_playoff_brackets.py --year "$year"

wait

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_in_playoff_bracket.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/in_playoff_bracket.html -c "NSBL $year - Current Playoff Bracket (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/in_playoff_bracket.html"

csvtotable /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs/NSBL_in_playoff_probabilities.csv /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/in_playoff_probabilities.html -c "NSBL $year - Current Playoff Probabilities (Last Updated $updateDate)" -vs 15 -o
python /Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/google_analytics_appender.py --file_path "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/Tables/in_playoff_probabilities.html"


wait


cd ~/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/
git add Tables/*
git add csvs/*
git add i/NSBL_WeeklyProjections/*
git commit -m "playoff NSBL update ($updateDate)"
git push