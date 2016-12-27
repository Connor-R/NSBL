from py_db import db

#Creates MySQL tables for league average statistics over a range of years

#This is an initialization script, and only needs to be run once, prior to running every other script

db = db('NSBL')


q = """
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

CREATE TABLE `processed_compWAR_offensive` (
    `year` int(11) NOT NULL,
    `team_abb` varchar(5) NOT NULL DEFAULT '',
    `player_name` varchar(50) NOT NULL DEFAULT '',
    `position` varchar(5) NOT NULL DEFAULT '',
    `bats` varchar(5) DEFAULT NULL,
    `age` int(3) NOT NULL,
    `pa` int(5) DEFAULT NULL,
    `pf` decimal(32,4) DEFAULT NULL,
    `wOBA` decimal(6,4) DEFAULT NULL,
    `park_wOBA` decimal(6,4) DEFAULT NULL,
    `OPS` decimal(6,4) DEFAULT NULL,
    `OPS_plus` decimal(6,2) DEFAULT NULL,
    `babip` decimal(5,3) DEFAULT NULL,
    `wRC` decimal(5,2) DEFAULT NULL,
    `wRC_27` decimal (5,3) DEFAULT NULL,
    `wRC_plus` decimal(6,2) DEFAULT NULL,
    `rAA` decimal(5,2) DEFAULT NULL,
    `oWAR` decimal(5,2) DEFAULT NULL,
    PRIMARY KEY (`year`,`team_abb`,`player_name`,`position`,`bats`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `processed_compWAR_defensive` (
    `year` int(11) NOT NULL,
    `team_abb` varchar(5) NOT NULL DEFAULT '',
    `player_name` varchar(50) NOT NULL DEFAULT '',
    `position` varchar(5) NOT NULL DEFAULT '',
    `bats` varchar(5) DEFAULT NULL,
    `age` int(3) NOT NULL,
    `pa` int(5)  DEFAULT NULL,
    `inn` decimal(6,1) DEFAULT NULL,
    `defense` decimal(6,3) DEFAULT NULL,
    `position_adj` decimal(6,3) DEFAULT NULL,
    `dWAR` decimal(5,2) DEFAULT NULL,
    PRIMARY KEY (`year`,`team_abb`,`player_name`,`position`,`bats`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
        


CREATE TABLE `processed_WAR_hitters` (
    `year` int(11) NOT NULL,
    `team_abb` varchar(5) NOT NULL DEFAULT '',
    `player_name` varchar(50) NOT NULL DEFAULT '',
    `position` varchar(5) NOT NULL DEFAULT '',
    `bats` varchar(5) DEFAULT NULL,
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


CREATE TABLE `processed_WAR_pitchers` (
    `year` int(11) NOT NULL,
    `team_abb` varchar(5) NOT NULL DEFAULT '',
    `player_name` varchar(50) NOT NULL DEFAULT '',
    `position` varchar(5) NOT NULL DEFAULT '',
    `throws` varchar(5) DEFAULT NULL,
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
"""


db.query(q)
