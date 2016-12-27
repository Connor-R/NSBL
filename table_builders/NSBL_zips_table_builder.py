from py_db import db

#Creates MySQL tables for importing ZiPS defensive ratings for a given year

#This should be run once before each season (with the correct year value)

db = db('NSBL')

year = str(2017)

print year
q = """
CREATE TABLE `zips_defense_"""+year+"""` (
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
    PRIMARY KEY (`player_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `zips_offense_"""+year+"""` (
    `player_name` varchar(50) NOT NULL DEFAULT '',
    `team_abb` varchar(5) NOT NULL DEFAULT '',
    `g` INT(11) DEFAULT NULL,
    `ab` INT(11) DEFAULT NULL,
    `r` INT(11) DEFAULT NULL,
    `h` INT(11) DEFAULT NULL,
    `2b` INT(11) DEFAULT NULL,
    `3b` INT(11) DEFAULT NULL,
    `hr` INT(11) DEFAULT NULL,
    `rbi` INT(11) DEFAULT NULL,
    `bb` INT(11) DEFAULT NULL,
    `so` INT(11) DEFAULT NULL,
    `hbp` INT(11) DEFAULT NULL,
    `sb` INT(11) DEFAULT NULL,
    `cs` INT(11) DEFAULT NULL,
    `sh` INT(11) DEFAULT NULL,
    `sf` INT(11) DEFAULT NULL,
    `ibb` INT(11) DEFAULT NULL,
    PRIMARY KEY (`player_name`, `team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `zips_pitching_"""+year+"""` (
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


CREATE TABLE `zips_processed_WAR_hitters_"""+year+"""` (
    `player_name` varchar(50) NOT NULL DEFAULT '',
    `team_abb` varchar(5) NOT NULL DEFAULT '',
    `position` VARCHAR(5) NOT NULL DEFAULT '',
    `pf` decimal(32,4) DEFAULT NULL,
    `position_adj` DECIMAL (30,1) DEFAULT NULL,
    `defense` DECIMAL (30,4) DEFAULT NULL,
    `dWAR` DECIMAL (30,2) DEFAULT NULL,
    `park_wOBA` DECIMAL(30,4) DEFAULT NULL,
    `rAA` DECIMAL(30,4) DEFAULT NULL,
    `oWAR` DECIMAL (30,2) DEFAULT NULL,
    `WAR` DECIMAL (30,2) DEFAULT NULL,  
    PRIMARY KEY (`player_name`, `team_abb`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `zips_processed_WAR_pitchers_"""+year+"""` (
    `player_name` varchar(50) NOT NULL DEFAULT '',
    `team_abb` varchar(5) NOT NULL DEFAULT '',
    `pf` decimal(32,4) DEFAULT NULL,
    `ip` DECIMAL (30,1) DEFAULT NULL,
    `k_9` DECIMAL(30,3) DEFAULT NULL,
    `bb_9` DECIMAL(30,3) DEFAULT NULL,
    `k_bb` DECIMAL(30,3) DEFAULT NULL,
    `hr_9` DECIMAL(30,3) DEFAULT NULL,
    `FIP` DECIMAL(30,4) DEFAULT NULL,
    `park_FIP` DECIMAL(30,4) DEFAULT NULL,
    `FIP_minus` DECIMAL(30,2) DEFAULT NULL,
    `FIP_WAR` DECIMAL(30,3) DEFAULT NULL,
    `ERA` DECIMAL(30,2) DEFAULT NULL,
    `park_ERA` DECIMAL(30,4) DEFAULT NULL,
    `ERA_minus` DECIMAL(30,2) DEFAULT NULL,
    `ERA_WAR` DECIMAL(30,3) DEFAULT NULL,
    PRIMARY KEY (`player_name`, `team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
"""

db.query(q)
