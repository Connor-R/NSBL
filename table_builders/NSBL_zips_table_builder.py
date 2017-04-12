from py_db import db

#Creates MySQL tables for team-by-team ratings and statistics for a given year

#This is an initialization script, and only needs to be run once, prior to running every other script


db = db('NSBL')

q = """
-- Create syntax for TABLE 'zips_averages_hitting'
CREATE TABLE `zips_averages_hitting` (
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

-- Create syntax for TABLE 'zips_averages_pitching'
CREATE TABLE `zips_averages_pitching` (
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
  `k_9` decimal(5,3) DEFAULT NULL,
  `bb_9` decimal(5,3) DEFAULT NULL,
  `k_bb` decimal(5,3) DEFAULT NULL,
  `hr_9` decimal(5,3) DEFAULT NULL,
  `fip_const` decimal(6,4) DEFAULT NULL,
  PRIMARY KEY (`year`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_defense'
CREATE TABLE `zips_defense` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `c_range` varchar(5) DEFAULT NULL,
  `c_error` int(5) DEFAULT NULL,
  `1b_range` varchar(5) DEFAULT NULL,
  `1b_error` int(5) DEFAULT NULL,
  `2b_range` varchar(5) DEFAULT NULL,
  `2b_error` int(5) DEFAULT NULL,
  `3b_range` varchar(5) DEFAULT NULL,
  `3b_error` int(5) DEFAULT NULL,
  `ss_range` varchar(5) DEFAULT NULL,
  `ss_error` int(5) DEFAULT NULL,
  `lf_range` varchar(5) DEFAULT NULL,
  `lf_error` int(5) DEFAULT NULL,
  `cf_range` varchar(5) DEFAULT NULL,
  `cf_error` int(5) DEFAULT NULL,
  `rf_range` varchar(5) DEFAULT NULL,
  `rf_error` int(5) DEFAULT NULL,
  `c_arm` varchar(5) DEFAULT NULL,
  `of_arm` varchar(5) DEFAULT NULL,
  `c_pb` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_offense'
CREATE TABLE `zips_offense` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `bats` varchar(5) DEFAULT NULL,
  `g` int(11) DEFAULT NULL,
  `ab` int(11) DEFAULT NULL,
  `r` int(11) DEFAULT NULL,
  `h` int(11) DEFAULT NULL,
  `2b` int(11) DEFAULT NULL,
  `3b` int(11) DEFAULT NULL,
  `hr` int(11) DEFAULT NULL,
  `rbi` int(11) DEFAULT NULL,
  `bb` int(11) DEFAULT NULL,
  `so` int(11) DEFAULT NULL,
  `hbp` int(11) DEFAULT NULL,
  `sb` int(11) DEFAULT NULL,
  `cs` int(11) DEFAULT NULL,
  `sh` int(11) DEFAULT NULL,
  `sf` int(11) DEFAULT NULL,
  `ibb` int(11) DEFAULT NULL,
  `zWAR` decimal(32,1) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_offense_splits'
CREATE TABLE `zips_offense_splits` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `vs_hand` varchar(5) NOT NULL DEFAULT '',
  `ab` int(11) DEFAULT NULL,
  `h` int(11) DEFAULT NULL,
  `2b` int(11) DEFAULT NULL,
  `3b` int(11) DEFAULT NULL,
  `hr` int(11) DEFAULT NULL,
  `rbi` int(11) DEFAULT NULL,
  `bb` int(11) DEFAULT NULL,
  `so` int(11) DEFAULT NULL,
  `hbp` int(11) DEFAULT NULL,
  `ibb` int(11) DEFAULT NULL,
  `sh` int(11) DEFAULT NULL,
  `sf` int(11) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`vs_hand`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_pitching'
CREATE TABLE `zips_pitching` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `throws` varchar(5) DEFAULT NULL,
  `w` int(11) DEFAULT NULL,
  `l` int(11) DEFAULT NULL,
  `era` decimal(32,2) DEFAULT NULL,
  `g` int(11) DEFAULT NULL,
  `gs` int(11) DEFAULT NULL,
  `ip` decimal(32,1) DEFAULT NULL,
  `h` int(11) DEFAULT NULL,
  `r` int(11) DEFAULT NULL,
  `er` int(11) DEFAULT NULL,
  `hr` int(11) DEFAULT NULL,
  `bb` int(11) DEFAULT NULL,
  `so` int(11) DEFAULT NULL,
  `zWAR` decimal(32,1) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_pitching_splits'
CREATE TABLE `zips_pitching_splits` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `vs_hand` varchar(5) NOT NULL DEFAULT '',
  `ab` int(11) DEFAULT NULL,
  `h` int(11) DEFAULT NULL,
  `2b` int(11) DEFAULT NULL,
  `3b` int(11) DEFAULT NULL,
  `hr` int(11) DEFAULT NULL,
  `rbi` int(11) DEFAULT NULL,
  `bb` int(11) DEFAULT NULL,
  `so` int(11) DEFAULT NULL,
  `hbp` int(11) DEFAULT NULL,
  `ibb` int(11) DEFAULT NULL,
  `sh` int(11) DEFAULT NULL,
  `sf` int(11) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`vs_hand`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_WAR_hitters'
CREATE TABLE `zips_WAR_hitters` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `bats` varchar(5) DEFAULT NULL,
  `pf` decimal(32,4) DEFAULT NULL,
  `position_adj` decimal(30,1) DEFAULT NULL,
  `rn` varchar(5) DEFAULT NULL,
  `er` int(11) DEFAULT NULL,
  `arm` varchar(5) DEFAULT NULL,
  `pb` int(11) DEFAULT NULL,
  `DRS` decimal(30,3) DEFAULT NULL,
  `dWAR` decimal(30,3) DEFAULT NULL,
  `vsL_wRC_plus` decimal(30,3) DEFAULT NULL,
  `vsR_wRC_plus` decimal(30,3) DEFAULT NULL,
  `wRC_plus` decimal(30,3) DEFAULT NULL,
  `vsL_oWAR` decimal(30,3) DEFAULT NULL,
  `vsR_oWAR` decimal(30,3) DEFAULT NULL,
  `oWAR` decimal(30,3) DEFAULT NULL,
  `vsL_WAR` decimal(30,3) DEFAULT NULL,
  `vsR_WAR` decimal(30,3) DEFAULT NULL,
  `WAR` decimal(30,3) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_WAR_hitters_comp'
CREATE TABLE `zips_WAR_hitters_comp` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `pf` decimal(32,4) DEFAULT NULL,
  `pa` int(11) DEFAULT NULL,
  `babip` decimal(30,4) DEFAULT NULL,
  `OPS_plus` decimal(30,3) DEFAULT NULL,
  `park_wOBA` decimal(30,3) DEFAULT NULL,
  `wRC_plus` decimal(30,3) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_WAR_pitchers'
CREATE TABLE `zips_WAR_pitchers` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `pf` decimal(32,4) DEFAULT NULL,
  `ip` decimal(30,1) DEFAULT NULL,
  `k_9` decimal(30,3) DEFAULT NULL,
  `bb_9` decimal(30,3) DEFAULT NULL,
  `k_bb` decimal(30,3) DEFAULT NULL,
  `hr_9` decimal(30,3) DEFAULT NULL,
  `FIP` decimal(30,4) DEFAULT NULL,
  `park_FIP` decimal(30,4) DEFAULT NULL,
  `FIP_minus` decimal(30,2) DEFAULT NULL,
  `FIP_WAR` decimal(30,3) DEFAULT NULL,
  `ERA` decimal(30,2) DEFAULT NULL,
  `park_ERA` decimal(30,4) DEFAULT NULL,
  `ERA_minus` decimal(30,2) DEFAULT NULL,
  `ERA_WAR` decimal(30,3) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_WAR_pitchers_comp'
CREATE TABLE `zips_WAR_pitchers_comp` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `vs_hand` varchar(5) NOT NULL DEFAULT '',
  `pf` decimal(32,4) DEFAULT NULL,
  `pa` int(11) DEFAULT NULL,
  `babip` decimal(30,4) DEFAULT NULL,
  `OPS_plus_against` decimal(30,3) DEFAULT NULL,
  `park_wOBA_against` decimal(30,3) DEFAULT NULL,
  `wRC_plus_against` decimal(30,3) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`,`vs_hand`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
"""

db.query(q)

