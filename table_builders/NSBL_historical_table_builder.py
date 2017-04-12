from py_db import db

#Creates MySQL tables for the yearly draft and free agency tables

#This is an initialization script, and only needs to be run once, prior to running every other script

#The draft_picks and free_agency tables need to manually imported from csv each year



db = db('NSBL')

q = """-- Create syntax for TABLE 'current_rosters'
CREATE TABLE `current_rosters` (
  `year` int(11) NOT NULL,
  `team_id` varchar(32) NOT NULL,
  `player_name` varchar(50) NOT NULL,
  `position` varchar(5) NOT NULL,
  `age` int(3) NOT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'current_rosters_excel'
CREATE TABLE `current_rosters_excel` (
  `player_name` varchar(50) NOT NULL,
  `team_abb` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(50) NOT NULL DEFAULT '',
  `salary` decimal(32,3) NOT NULL,
  `year` varchar(50) NOT NULL DEFAULT '',
  `expires` int(12) NOT NULL DEFAULT '0',
  `option` varchar(50) NOT NULL DEFAULT '',
  `NTC` varchar(50) DEFAULT NULL,
  `salary_counted` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`player_name`,`salary`,`year`,`expires`,`option`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'historical_draft_picks'
CREATE TABLE `historical_draft_picks` (
  `year` int(11) NOT NULL,
  `season` varchar(5) NOT NULL,
  `overall` int(11) NOT NULL,
  `round` int(11) NOT NULL,
  `pick` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL,
  `player_name` varchar(50) NOT NULL,
  `position` varchar(5) NOT NULL,
  PRIMARY KEY (`year`,`season`,`overall`,`round`,`pick`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'historical_free_agency'
CREATE TABLE `historical_free_agency` (
  `year` int(11) NOT NULL,
  `day` varchar(32) NOT NULL,
  `signing_team` varchar(5) NOT NULL,
  `rights` varchar(5) NOT NULL DEFAULT '',
  `player_name` varchar(50) NOT NULL,
  `position` varchar(5) NOT NULL DEFAULT '',
  `contract_years` int(11) NOT NULL,
  `option` varchar(5) NOT NULL DEFAULT '',
  `aav` decimal(30,3) NOT NULL,
  PRIMARY KEY (`year`,`day`,`signing_team`,`player_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'historical_stats_hitters_advanced'
CREATE TABLE `historical_stats_hitters_advanced` (
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `years` bigint(21) NOT NULL DEFAULT '0',
  `pa` decimal(32,0) DEFAULT NULL,
  `defense` decimal(28,3) DEFAULT NULL,
  `position_adj` decimal(28,3) DEFAULT NULL,
  `dWAR` decimal(27,2) DEFAULT NULL,
  `park_wOBA` decimal(42,4) DEFAULT NULL,
  `OPS_plus` decimal(42,4) DEFAULT NULL,
  `wRC_plus` decimal(42,4) DEFAULT NULL,
  `rAA` decimal(27,3) DEFAULT NULL,
  `oWAR` decimal(27,2) DEFAULT NULL,
  `replacement` decimal(28,2) DEFAULT NULL,
  `WAR` decimal(28,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'historical_stats_hitters_primary'
CREATE TABLE `historical_stats_hitters_primary` (
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `years` bigint(21) NOT NULL DEFAULT '0',
  `pa` decimal(32,0) DEFAULT NULL,
  `ab` decimal(32,0) DEFAULT NULL,
  `avg` decimal(35,4) DEFAULT NULL,
  `obp` decimal(35,4) DEFAULT NULL,
  `slg` decimal(35,4) DEFAULT NULL,
  `h` decimal(32,0) DEFAULT NULL,
  `2b` decimal(32,0) DEFAULT NULL,
  `3b` decimal(32,0) DEFAULT NULL,
  `hr` decimal(32,0) DEFAULT NULL,
  `r` decimal(32,0) DEFAULT NULL,
  `rbi` decimal(32,0) DEFAULT NULL,
  `hbp` decimal(32,0) DEFAULT NULL,
  `bb` decimal(32,0) DEFAULT NULL,
  `k` decimal(32,0) DEFAULT NULL,
  `sb` decimal(32,0) DEFAULT NULL,
  `cs` decimal(32,0) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'historical_stats_pitchers_advanced'
CREATE TABLE `historical_stats_pitchers_advanced` (
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `years` bigint(21) NOT NULL DEFAULT '0',
  `ip` decimal(29,1) DEFAULT NULL,
  `k_9` decimal(39,2) DEFAULT NULL,
  `bb_9` decimal(39,2) DEFAULT NULL,
  `k_bb` decimal(39,2) DEFAULT NULL,
  `hr_9` decimal(39,2) DEFAULT NULL,
  `FIP` decimal(40,3) DEFAULT NULL,
  `park_FIP` decimal(40,3) DEFAULT NULL,
  `FIP_minus` decimal(40,2) DEFAULT NULL,
  `FIP_WAR` decimal(28,2) DEFAULT NULL,
  `ERA` decimal(40,3) DEFAULT NULL,
  `park_ERA` decimal(40,3) DEFAULT NULL,
  `ERA_minus` decimal(40,2) DEFAULT NULL,
  `ERA_WAR` decimal(28,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'historical_stats_pitchers_primary'
CREATE TABLE `historical_stats_pitchers_primary` (
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `years` bigint(21) NOT NULL DEFAULT '0',
  `era` decimal(35,4) DEFAULT NULL,
  `w` decimal(32,0) DEFAULT NULL,
  `l` decimal(32,0) DEFAULT NULL,
  `sv` decimal(32,0) DEFAULT NULL,
  `g` decimal(32,0) DEFAULT NULL,
  `gs` decimal(32,0) DEFAULT NULL,
  `cg` decimal(32,0) DEFAULT NULL,
  `sho` decimal(32,0) DEFAULT NULL,
  `ip` decimal(33,1) DEFAULT NULL,
  `h` decimal(32,0) DEFAULT NULL,
  `r` decimal(32,0) DEFAULT NULL,
  `er` decimal(32,0) DEFAULT NULL,
  `bb` decimal(32,0) DEFAULT NULL,
  `k` decimal(32,0) DEFAULT NULL,
  `hr` decimal(32,0) DEFAULT NULL,
  `gdp` decimal(32,0) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
"""

db.query(q)
