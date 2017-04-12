from py_db import db

#Creates MySQL tables for team-by-team ratings and statistics for a given year

#This is an initialization script, and only needs to be run once, prior to running every other script


db = db('NSBL')

q = """-- Create syntax for TABLE 'register_batting_analytical'
CREATE TABLE `register_batting_analytical` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `age` int(5) NOT NULL DEFAULT '0',
  `pa/g` decimal(4,2) DEFAULT NULL,
  `ab/g` decimal(4,2) DEFAULT NULL,
  `bip` int(5) DEFAULT NULL,
  `babip` decimal(4,3) DEFAULT NULL,
  `tbw` int(5) DEFAULT NULL,
  `tbw/pa` decimal(5,3) DEFAULT NULL,
  `tbwh` int(5) DEFAULT NULL,
  `tbwh/pa` decimal(5,3) DEFAULT NULL,
  `k/bb` decimal(5,1) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`,`position`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'register_batting_primary'
CREATE TABLE `register_batting_primary` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `age` int(5) NOT NULL DEFAULT '0',
  `avg` decimal(4,3) DEFAULT NULL,
  `obp` decimal(4,3) DEFAULT NULL,
  `slg` decimal(4,3) DEFAULT NULL,
  `ab` int(5) DEFAULT NULL,
  `h` int(5) DEFAULT NULL,
  `2b` int(5) DEFAULT NULL,
  `3b` int(5) DEFAULT NULL,
  `hr` int(5) DEFAULT NULL,
  `r` int(5) DEFAULT NULL,
  `rbi` int(5) DEFAULT NULL,
  `hbp` int(5) DEFAULT NULL,
  `bb` int(5) DEFAULT NULL,
  `k` int(5) DEFAULT NULL,
  `sb` int(5) DEFAULT NULL,
  `cs` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`,`position`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'register_batting_secondary'
CREATE TABLE `register_batting_secondary` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `age` int(5) NOT NULL DEFAULT '0',
  `gs` int(5) DEFAULT NULL,
  `pa` int(5) DEFAULT NULL,
  `sh` int(5) DEFAULT NULL,
  `sf` int(5) DEFAULT NULL,
  `gdp` int(5) DEFAULT NULL,
  `ops` decimal(5,3) DEFAULT NULL,
  `rc` decimal(5,1) DEFAULT NULL,
  `rc27` decimal(4,1) DEFAULT NULL,
  `iso` decimal(5,3) DEFAULT NULL,
  `tavg` decimal(5,3) DEFAULT NULL,
  `sec` decimal(5,3) DEFAULT NULL,
  `xbh` int(5) DEFAULT NULL,
  `tb` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`,`position`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'register_batting_splits'
CREATE TABLE `register_batting_splits` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `age` int(5) NOT NULL DEFAULT '0',
  `vs_hand` varchar(5) NOT NULL DEFAULT '',
  `avg` decimal(4,3) DEFAULT NULL,
  `obp` decimal(4,3) DEFAULT NULL,
  `slg` decimal(4,3) DEFAULT NULL,
  `ops` decimal(4,3) DEFAULT NULL,
  `ab` int(5) DEFAULT NULL,
  `h` int(5) DEFAULT NULL,
  `2b` int(5) DEFAULT NULL,
  `3b` int(5) DEFAULT NULL,
  `hr` int(5) DEFAULT NULL,
  `rbi` int(5) DEFAULT NULL,
  `bb` int(5) DEFAULT NULL,
  `k` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`,`position`,`age`,`vs_hand`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'register_pitching_analytical'
CREATE TABLE `register_pitching_analytical` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `age` int(5) NOT NULL DEFAULT '0',
  `ops` decimal(5,4) DEFAULT NULL,
  `bip` int(5) DEFAULT NULL,
  `babip` decimal(5,4) DEFAULT NULL,
  `tbw` int(5) DEFAULT NULL,
  `tbw/bf` decimal(5,4) DEFAULT NULL,
  `tbwh` int(5) DEFAULT NULL,
  `tbwh/bf` decimal(5,4) DEFAULT NULL,
  `rc` decimal(5,1) DEFAULT NULL,
  `rc27` decimal(5,1) DEFAULT NULL,
  `rcera` decimal(5,2) DEFAULT NULL,
  `cera` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`,`position`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'register_pitching_primary'
CREATE TABLE `register_pitching_primary` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `age` int(5) NOT NULL DEFAULT '0',
  `era` decimal(5,2) DEFAULT NULL,
  `w` int(5) DEFAULT NULL,
  `l` int(5) DEFAULT NULL,
  `sv` int(5) DEFAULT NULL,
  `g` int(5) DEFAULT NULL,
  `gs` int(5) DEFAULT NULL,
  `cg` int(5) DEFAULT NULL,
  `sho` int(5) DEFAULT NULL,
  `ip` decimal(5,1) DEFAULT NULL,
  `h` int(5) DEFAULT NULL,
  `r` int(5) DEFAULT NULL,
  `er` int(5) DEFAULT NULL,
  `bb` int(5) DEFAULT NULL,
  `k` int(5) DEFAULT NULL,
  `hr` int(5) DEFAULT NULL,
  `gdp` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`,`position`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'register_pitching_rates_relief'
CREATE TABLE `register_pitching_rates_relief` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `age` int(5) NOT NULL DEFAULT '0',
  `svo` int(5) DEFAULT NULL,
  `sv` int(5) DEFAULT NULL,
  `sv_pct` decimal(5,4) DEFAULT NULL,
  `bs` int(5) DEFAULT NULL,
  `bs_pct` decimal(5,4) DEFAULT NULL,
  `hld` int(5) DEFAULT NULL,
  `ir` int(5) DEFAULT NULL,
  `irs` int(5) DEFAULT NULL,
  `ir_pct` decimal(5,4) DEFAULT NULL,
  `g` int(5) DEFAULT NULL,
  `gr` int(5) DEFAULT NULL,
  `gf` int(5) DEFAULT NULL,
  `pch/g` decimal(5,1) DEFAULT NULL,
  `str_pct` decimal(5,4) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`,`position`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'register_pitching_rates_start'
CREATE TABLE `register_pitching_rates_start` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `age` int(5) NOT NULL DEFAULT '0',
  `gs` int(5) DEFAULT NULL,
  `cg` int(5) DEFAULT NULL,
  `cg_pct` decimal(5,4) DEFAULT NULL,
  `sho` int(5) DEFAULT NULL,
  `qs` int(5) DEFAULT NULL,
  `qs_pct` decimal(5,4) DEFAULT NULL,
  `rs` int(5) DEFAULT NULL,
  `rs/g` decimal(5,1) DEFAULT NULL,
  `rl` int(5) DEFAULT NULL,
  `rls` int(5) DEFAULT NULL,
  `rl_pct` decimal(5,4) DEFAULT NULL,
  `pch/g` decimal(5,1) DEFAULT NULL,
  `str_pct` decimal(5,4) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`,`position`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'register_pitching_secondary'
CREATE TABLE `register_pitching_secondary` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `age` int(5) NOT NULL DEFAULT '0',
  `sb` int(5) DEFAULT NULL,
  `cs` int(5) DEFAULT NULL,
  `ibb` int(5) DEFAULT NULL,
  `hbp` int(5) DEFAULT NULL,
  `wp` int(5) DEFAULT NULL,
  `bk` int(5) DEFAULT NULL,
  `sh` int(5) DEFAULT NULL,
  `sf` int(5) DEFAULT NULL,
  `h/9` decimal(5,1) DEFAULT NULL,
  `bb/9` decimal(5,1) DEFAULT NULL,
  `r/9` decimal(5,1) DEFAULT NULL,
  `k/9` decimal(5,1) DEFAULT NULL,
  `hr/9` decimal(5,1) DEFAULT NULL,
  `k/bb` decimal(5,1) DEFAULT NULL,
  `whip` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`,`position`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
"""

db.query(q)

