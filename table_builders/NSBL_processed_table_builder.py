from py_db import db

#Creates MySQL tables for team-by-team ratings and statistics for a given year

#This is an initialization script, and only needs to be run once, prior to running every other script


db = db('NSBL')

q = """
-- Create syntax for TABLE 'processed_advanced_standings'
CREATE TABLE `processed_advanced_standings` (
  `year` int(11) NOT NULL,
  `team_name` varchar(32) NOT NULL DEFAULT '',
  `repWAR` decimal(32,2) DEFAULT NULL,
  `oWAR` decimal(32,2) DEFAULT NULL,
  `dWAR` decimal(32,2) DEFAULT NULL,
  `FIP_WAR` decimal(32,2) DEFAULT NULL,
  `ERA_WAR` decimal(32,2) DEFAULT NULL,
  `RF` int(11) DEFAULT NULL,
  `RA` int(11) DEFAULT NULL,
  `f_Wins` decimal(32,2) DEFAULT NULL,
  `f_Losses` decimal(32,2) DEFAULT NULL,
  `r_Wins` decimal(32,2) DEFAULT NULL,
  `r_Losses` decimal(32,2) DEFAULT NULL,
  `py_Wins` decimal(32,2) DEFAULT NULL,
  `py_Losses` decimal(32,2) DEFAULT NULL,
  `W` int(11) DEFAULT NULL,
  `L` int(11) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_compWAR_defensive'
CREATE TABLE `processed_compWAR_defensive` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `bats` varchar(5) NOT NULL DEFAULT '',
  `age` int(3) NOT NULL,
  `pa` int(5) DEFAULT NULL,
  `inn` decimal(6,1) DEFAULT NULL,
  `defense` decimal(6,3) DEFAULT NULL,
  `position_adj` decimal(6,3) DEFAULT NULL,
  `dWAR` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_abb`,`player_name`,`position`,`bats`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_compWAR_offensive'
CREATE TABLE `processed_compWAR_offensive` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `bats` varchar(5) NOT NULL DEFAULT '',
  `age` int(3) NOT NULL,
  `pa` int(5) DEFAULT NULL,
  `pf` decimal(32,4) DEFAULT NULL,
  `wOBA` decimal(6,4) DEFAULT NULL,
  `park_wOBA` decimal(6,4) DEFAULT NULL,
  `OPS` decimal(6,4) DEFAULT NULL,
  `OPS_plus` decimal(6,2) DEFAULT NULL,
  `babip` decimal(5,3) DEFAULT NULL,
  `wRC` decimal(5,2) DEFAULT NULL,
  `wRC_27` decimal(5,3) DEFAULT NULL,
  `wRC_plus` decimal(6,2) DEFAULT NULL,
  `rAA` decimal(5,2) DEFAULT NULL,
  `oWAR` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_abb`,`player_name`,`position`,`bats`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_league_averages_hitting'
CREATE TABLE `processed_league_averages_hitting` (
  `year` int(11) NOT NULL,
  `pa` int(11) DEFAULT NULL,
  `ab` int(11) DEFAULT NULL,
  `h` int(11) DEFAULT NULL,
  `1b` int(11) DEFAULT NULL,
  `2b` int(11) DEFAULT NULL,
  `3b` int(11) DEFAULT NULL,
  `hr` int(11) DEFAULT NULL,
  `r` int(11) DEFAULT NULL,
  `rbi` int(11) DEFAULT NULL,
  `hbp` int(11) DEFAULT NULL,
  `bb` int(11) DEFAULT NULL,
  `k` int(11) DEFAULT NULL,
  `sb` int(11) DEFAULT NULL,
  `cs` int(11) DEFAULT NULL,
  `wOBA` decimal(5,4) DEFAULT NULL,
  `babip` decimal(5,4) DEFAULT NULL,
  `rc` decimal(7,1) DEFAULT NULL,
  `rc_27` decimal(5,3) DEFAULT NULL,
  PRIMARY KEY (`year`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_league_averages_pitching'
CREATE TABLE `processed_league_averages_pitching` (
  `year` int(11) NOT NULL,
  `era` decimal(6,4) DEFAULT NULL,
  `w` int(11) DEFAULT NULL,
  `l` int(11) DEFAULT NULL,
  `sv` int(11) DEFAULT NULL,
  `g` int(11) DEFAULT NULL,
  `gs` int(11) DEFAULT NULL,
  `cg` int(11) DEFAULT NULL,
  `sho` int(11) DEFAULT NULL,
  `ip` decimal(7,1) DEFAULT NULL,
  `h` int(11) DEFAULT NULL,
  `r` int(11) DEFAULT NULL,
  `er` int(11) DEFAULT NULL,
  `bb` int(11) DEFAULT NULL,
  `k` int(11) DEFAULT NULL,
  `hr` int(11) DEFAULT NULL,
  `gdp` int(11) DEFAULT NULL,
  `k_9` decimal(5,3) DEFAULT NULL,
  `bb_9` decimal(5,3) DEFAULT NULL,
  `k_bb` decimal(5,3) DEFAULT NULL,
  `hr_9` decimal(5,3) DEFAULT NULL,
  `fip_const` decimal(6,4) DEFAULT NULL,
  PRIMARY KEY (`year`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_WAR_hitters'
CREATE TABLE `processed_WAR_hitters` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `bats` varchar(5) NOT NULL DEFAULT '',
  `age` int(3) NOT NULL,
  `pa` int(5) DEFAULT NULL,
  `defense` decimal(6,3) DEFAULT NULL,
  `position_adj` decimal(6,3) DEFAULT NULL,
  `dWAR` decimal(5,2) DEFAULT NULL,
  `oWAR` decimal(5,2) DEFAULT NULL,
  `replacement` decimal(6,3) DEFAULT NULL,
  `WAR` decimal(6,3) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_abb`,`player_name`,`position`,`bats`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_WAR_pitchers'
CREATE TABLE `processed_WAR_pitchers` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `throws` varchar(5) NOT NULL DEFAULT '',
  `age` int(3) NOT NULL,
  `ip` decimal(7,1) DEFAULT NULL,
  `pf` decimal(32,4) DEFAULT NULL,
  `k_9` decimal(5,3) DEFAULT NULL,
  `bb_9` decimal(5,3) DEFAULT NULL,
  `k_bb` decimal(5,3) DEFAULT NULL,
  `hr_9` decimal(5,3) DEFAULT NULL,
  `FIP` decimal(6,4) DEFAULT NULL,
  `park_FIP` decimal(6,4) DEFAULT NULL,
  `FIP_minus` decimal(6,2) DEFAULT NULL,
  `FIP_WAR` decimal(6,3) DEFAULT NULL,
  `ERA` decimal(6,4) DEFAULT NULL,
  `park_ERA` decimal(6,4) DEFAULT NULL,
  `ERA_minus` decimal(6,2) DEFAULT NULL,
  `ERA_WAR` decimal(6,3) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_abb`,`player_name`,`position`,`throws`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_WAR_team'
CREATE TABLE `processed_WAR_team` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `defense` decimal(6,3) DEFAULT NULL,
  `position_adj` decimal(6,3) DEFAULT NULL,
  `dWAR` decimal(6,3) DEFAULT NULL,
  `oWAR` decimal(6,3) DEFAULT NULL,
  `replacement` decimal(6,3) DEFAULT NULL,
  `hitter_WAR` decimal(6,3) DEFAULT NULL,
  `FIP_WAR` decimal(6,3) DEFAULT NULL,
  `ERA_WAR` decimal(6,3) DEFAULT NULL,
  `total_fWAR` decimal(6,3) DEFAULT NULL,
  `total_rWAR` decimal(6,3) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
"""

db.query(q)

