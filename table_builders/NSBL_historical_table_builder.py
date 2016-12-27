from py_db import db

#Creates MySQL tables for the yearly draft and free agency tables

#This is an initialization script, and only needs to be run once, prior to running every other script

#The draft_picks and free_agency tables need to manually imported from csv each year



db = db('NSBL')

q = """
CREATE TABLE `historical_draft_picks` (
    `year` int(11) NOT NULL,
    `season` varchar(5) NOT NULL DEFAULT '',
    `overall` int(11) NOT NULL DEFAULT '',
    `round` int(11) NOT NULL DEFAULT '',
    `pick` int(11) NOT NULL DEFAULT '',
    `team_abb` varchar(5) NOT NULL,
    `player_name` varchar(50) NOT NULL,
    `position` varchar(5) NOT NULL,
    PRIMARY KEY (`year`,`season`,`overall`,`round`,`pick`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `historical_free_agency` (
    `year` int(11) NOT NULL,
    `day` varchar(32) NOT NULL,
    `signing_team` varchar(5) NOT NULL,
    `rights` varchar(5) NOT NULL DEFAULT '',
    `player_name` varchar(50) NOT NULL,
    `position` varchar(5) NOT NULL DEFAULT '',
    `contract_years` int(11) NOT NULL,
    `option` varchar(5) NOT NULL DEFAULT '',
    `aav` DECIMAL(30,3) NOT NULL,
    PRIMARY KEY (`year`,`day`,`signing_team`,`player_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
"""

db.query(q)
