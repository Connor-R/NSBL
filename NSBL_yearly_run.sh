# Shell script to run at the start of each year to build the relevant tables in the db

python table_builders/NSBL_zips_table_builder.py

wait
# import defense, hitting, and pitching csvs

python processing/zips_processed_WAR_hitters.py
python processing/zips_processed_WAR_pitchers.py