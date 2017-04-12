# Shell script to run at the start of each year to build the relevant tables in the db

python processing/zips_import_projections.py
python processing/zips_import_projections_splits.py

wait

python processing/zips_WAR_pitchers.py
python processing/zips_WAR_pitchers_comp.py
python processing/zips_WAR_hitters.py
python processing/zips_WAR_hitters_comp.py