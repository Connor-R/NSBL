from py_db import db

#Creates MySQL tables for team-by-team ratings and statistics for a given year

#This is an initialization script, and only needs to be run once, prior to running every other script


db = db('NSBL')

q = """
-- Create syntax for TABLE '_draft_prospects'
CREATE TABLE `_draft_prospects` (
  `year` int(11) unsigned NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `player_id` varchar(64) NOT NULL DEFAULT '',
  `fname` text,
  `lname` text,
  `team` text,
  `position` text,
  `bats` text,
  `throws` text,
  `height` int(11) DEFAULT NULL,
  `weight` int(11) DEFAULT NULL,
  `drafted` text,
  `signed` int(11) DEFAULT NULL,
  `pre_top100` int(11) DEFAULT NULL,
  `eta` int(11) DEFAULT NULL,
  `twitter` text,
  `blurb` text,
  PRIMARY KEY (`year`,`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '_international_prospects'
CREATE TABLE `_international_prospects` (
  `year` int(11) unsigned NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `player_id` varchar(64) NOT NULL DEFAULT '',
  `fname` text,
  `lname` text,
  `team` text,
  `position` text,
  `bats` text,
  `throws` text,
  `height` int(11) DEFAULT NULL,
  `weight` int(11) DEFAULT NULL,
  `drafted` text,
  `signed` int(11) DEFAULT NULL,
  `pre_top100` int(11) DEFAULT NULL,
  `eta` int(11) DEFAULT NULL,
  `twitter` text,
  `blurb` text,
  PRIMARY KEY (`year`,`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '_professional_prospects'
CREATE TABLE `_professional_prospects` (
  `year` int(11) unsigned NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `player_id` int(11) NOT NULL,
  `fname` text,
  `lname` text,
  `team` text,
  `position` text,
  `bats` text,
  `throws` text,
  `height` int(11) DEFAULT NULL,
  `weight` int(11) DEFAULT NULL,
  `drafted` text,
  `signed` text,
  `pre_top100` int(11) DEFAULT NULL,
  `eta` int(11) DEFAULT NULL,
  `twitter` text,
  `blurb` text,
  PRIMARY KEY (`year`,`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '_prospect_hitter_grades'
CREATE TABLE `_prospect_hitter_grades` (
  `year` int(11) NOT NULL DEFAULT '0',
  `player_id` varchar(64) NOT NULL DEFAULT '',
  `hit` int(11) DEFAULT NULL,
  `power` int(11) DEFAULT NULL,
  `run` int(11) DEFAULT NULL,
  `arm` int(11) DEFAULT NULL,
  `field` int(11) DEFAULT NULL,
  `overall` int(11) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '_prospect_pitcher_grades'
CREATE TABLE `_prospect_pitcher_grades` (
  `year` int(11) NOT NULL DEFAULT '0',
  `player_id` varchar(64) NOT NULL DEFAULT '',
  `fastball` int(11) DEFAULT NULL,
  `change` int(11) DEFAULT NULL,
  `curve` int(11) DEFAULT NULL,
  `slider` int(11) DEFAULT NULL,
  `cutter` int(11) DEFAULT NULL,
  `splitter` int(11) DEFAULT NULL,
  `other` int(11) DEFAULT NULL,
  `control` int(11) DEFAULT NULL,
  `overall` int(11) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'ratings_batting'
CREATE TABLE `ratings_batting` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `bats` varchar(5) DEFAULT NULL,
  `age` int(3) NOT NULL,
  `vsL_avg` decimal(3,3) DEFAULT NULL,
  `vsL_pwr` varchar(5) DEFAULT NULL,
  `vsR_avg` decimal(3,3) DEFAULT NULL,
  `vsR_pwr` varchar(5) DEFAULT NULL,
  `bunt_sac` varchar(5) DEFAULT NULL,
  `bunt_hit` varchar(5) DEFAULT NULL,
  `run` varchar(5) DEFAULT NULL,
  `steal` varchar(5) DEFAULT NULL,
  `jump` varchar(5) DEFAULT NULL,
  `injury` varchar(20) DEFAULT NULL,
  `clutch` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'ratings_fielding'
CREATE TABLE `ratings_fielding` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `p` text,
  `c` text,
  `1b` text,
  `2b` text,
  `3b` text,
  `ss` text,
  `lf` text,
  `cf` text,
  `rf` text,
  `thr_of` varchar(5) DEFAULT '',
  `thr_c` varchar(5) DEFAULT NULL,
  `pb` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'ratings_pitching'
CREATE TABLE `ratings_pitching` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `throws` varchar(5) DEFAULT NULL,
  `age` int(3) NOT NULL,
  `vsL_avg` decimal(3,3) DEFAULT NULL,
  `vsR_avg` decimal(3,3) DEFAULT NULL,
  `bunt_sac` varchar(5) DEFAULT NULL,
  `bunt_hit` varchar(5) DEFAULT NULL,
  `run` varchar(5) DEFAULT NULL,
  `steal` varchar(5) DEFAULT NULL,
  `jump` varchar(5) DEFAULT NULL,
  `dur_s` varchar(5) DEFAULT NULL,
  `dur_r` varchar(5) DEFAULT NULL,
  `hld` varchar(5) DEFAULT NULL,
  `wp` int(3) DEFAULT NULL,
  `bk` int(3) DEFAULT NULL,
  `gb_pct` int(3) DEFAULT NULL,
  `jam` varchar(20) DEFAULT NULL,
  `injury` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_batting_analytical'
CREATE TABLE `statistics_batting_analytical` (
  `year` int(11) NOT NULL,
  `team_Id` int(11) unsigned NOT NULL DEFAULT '0',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `pa/g` decimal(4,2) DEFAULT NULL,
  `ab/g` decimal(4,2) DEFAULT NULL,
  `bip` int(5) DEFAULT NULL,
  `babip` decimal(4,3) DEFAULT NULL,
  `tbw` int(5) DEFAULT NULL,
  `tbw/pa` decimal(5,3) DEFAULT NULL,
  `tbwh` int(5) DEFAULT NULL,
  `tbwh/pa` decimal(5,3) DEFAULT NULL,
  `k/bb` decimal(5,1) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_Id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_batting_primary'
CREATE TABLE `statistics_batting_primary` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `avg` decimal(4,3) DEFAULT NULL,
  `obp` decimal(4,3) DEFAULT NULL,
  `slg` decimal(4,3) DEFAULT NULL,
  `g` int(5) DEFAULT NULL,
  `ab` int(5) DEFAULT NULL,
  `h` int(5) DEFAULT NULL,
  `2b` int(5) DEFAULT NULL,
  `3b` int(5) DEFAULT NULL,
  `hr` int(5) DEFAULT NULL,
  `r` int(5) DEFAULT NULL,
  `rbi` int(5) DEFAULT NULL,
  `bb` int(5) DEFAULT NULL,
  `k` int(5) DEFAULT NULL,
  `hbp` int(5) DEFAULT NULL,
  `ibb` int(5) DEFAULT NULL,
  `sb` int(5) DEFAULT NULL,
  `cs` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_batting_secondary'
CREATE TABLE `statistics_batting_secondary` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL DEFAULT '0',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `gs` int(5) DEFAULT NULL,
  `pa` int(5) DEFAULT NULL,
  `sh` int(5) DEFAULT NULL,
  `sf` int(5) DEFAULT NULL,
  `gdp` int(5) DEFAULT NULL,
  `gw` int(5) DEFAULT NULL,
  `ci` int(5) DEFAULT NULL,
  `ops` decimal(5,3) DEFAULT NULL,
  `rc` decimal(5,1) DEFAULT NULL,
  `rc27` decimal(4,1) DEFAULT NULL,
  `iso` decimal(5,3) DEFAULT NULL,
  `tavg` decimal(5,3) DEFAULT NULL,
  `sec` decimal(5,3) DEFAULT NULL,
  `xbh` int(5) DEFAULT NULL,
  `tb` int(5) DEFAULT NULL,
  `chs` int(5) DEFAULT NULL,
  `lhs` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_batting_splits'
CREATE TABLE `statistics_batting_splits` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
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
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`,`vs_hand`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_fielding'
CREATE TABLE `statistics_fielding` (
  `year` int(11) NOT NULL,
  `team_id` int(11) NOT NULL DEFAULT '0',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `pos` varchar(5) NOT NULL DEFAULT '',
  `g` int(5) DEFAULT NULL,
  `gs` int(5) DEFAULT NULL,
  `inn` decimal(6,1) DEFAULT NULL,
  `po` int(5) DEFAULT NULL,
  `a` int(5) DEFAULT NULL,
  `e` int(5) DEFAULT NULL,
  `dp` int(5) DEFAULT NULL,
  `tc` int(5) DEFAULT NULL,
  `f_pct` decimal(5,3) DEFAULT NULL,
  `pb` int(5) DEFAULT NULL,
  `sb` int(5) DEFAULT NULL,
  `cs` int(5) DEFAULT NULL,
  `sb_pct` decimal(5,3) DEFAULT NULL,
  `pk` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`pos`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_pitching_analytical'
CREATE TABLE `statistics_pitching_analytical` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL DEFAULT '0',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `ops` decimal(5,3) DEFAULT NULL,
  `whip` decimal(5,2) DEFAULT NULL,
  `bip` int(5) DEFAULT NULL,
  `babip` decimal(5,3) DEFAULT NULL,
  `tbw` int(5) DEFAULT NULL,
  `tbw/bf` decimal(5,3) DEFAULT NULL,
  `tbwh` int(5) DEFAULT NULL,
  `tbwh/bf` decimal(5,3) DEFAULT NULL,
  `rc` decimal(5,1) DEFAULT NULL,
  `rc27` decimal(5,1) DEFAULT NULL,
  `rcera` decimal(5,2) DEFAULT NULL,
  `cera` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_pitching_primary'
CREATE TABLE `statistics_pitching_primary` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL DEFAULT '0',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
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
  `bf` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_pitching_rates_relief'
CREATE TABLE `statistics_pitching_rates_relief` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL DEFAULT '0',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `svo` int(5) DEFAULT NULL,
  `sv` int(5) DEFAULT NULL,
  `sv_pct` decimal(5,3) DEFAULT NULL,
  `bs` int(5) DEFAULT NULL,
  `bs_pct` decimal(5,3) DEFAULT NULL,
  `hld` int(5) DEFAULT NULL,
  `ir` int(5) DEFAULT NULL,
  `irs` int(5) DEFAULT NULL,
  `ir_pct` decimal(5,3) DEFAULT NULL,
  `g` int(5) DEFAULT NULL,
  `gr` int(5) DEFAULT NULL,
  `gf` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_pitching_rates_start'
CREATE TABLE `statistics_pitching_rates_start` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL DEFAULT '0',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `gs` int(5) DEFAULT NULL,
  `cg` int(5) DEFAULT NULL,
  `cg_pct` decimal(5,3) DEFAULT NULL,
  `sho` int(5) DEFAULT NULL,
  `qs` int(5) DEFAULT NULL,
  `qs_pct` decimal(5,3) DEFAULT NULL,
  `rs` int(5) DEFAULT NULL,
  `rs/g` decimal(5,1) DEFAULT NULL,
  `rl` int(5) DEFAULT NULL,
  `rls` int(5) DEFAULT NULL,
  `rl_pct` decimal(5,3) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_pitching_secondary'
CREATE TABLE `statistics_pitching_secondary` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL DEFAULT '0',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `sb` int(5) DEFAULT NULL,
  `cs` int(5) DEFAULT NULL,
  `ibb` int(5) DEFAULT NULL,
  `hbp` int(5) DEFAULT NULL,
  `wp` int(5) DEFAULT NULL,
  `bk` int(5) DEFAULT NULL,
  `sh` int(5) DEFAULT NULL,
  `sf` int(5) DEFAULT NULL,
  `ci` int(5) DEFAULT NULL,
  `h/9` decimal(5,1) DEFAULT NULL,
  `bb/9` decimal(5,1) DEFAULT NULL,
  `r/9` decimal(5,1) DEFAULT NULL,
  `k/9` decimal(5,1) DEFAULT NULL,
  `hr/9` decimal(5,1) DEFAULT NULL,
  `k/bb` decimal(5,1) DEFAULT NULL,
  `pch/g` decimal(5,1) DEFAULT NULL,
  `str_pct` decimal(5,3) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_pitching_splits'
CREATE TABLE `statistics_pitching_splits` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
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
  `hbp` int(5) DEFAULT NULL,
  `bb` int(5) DEFAULT NULL,
  `ibb` int(5) DEFAULT NULL,
  `k` int(5) DEFAULT NULL,
  `sh` int(5) DEFAULT NULL,
  `sf` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`,`player_name`,`position`,`vs_hand`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'statistics_pitching_splits_primary'
CREATE TABLE `statistics_pitching_splits_primary` (
  `year` int(11) NOT NULL,
  `team_Id` int(11) unsigned NOT NULL DEFAULT '0',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `avg` decimal(5,3) DEFAULT NULL,
  `obp` decimal(5,3) DEFAULT NULL,
  `slg` decimal(5,3) DEFAULT NULL,
  `ab` int(5) DEFAULT NULL,
  `h` int(5) DEFAULT NULL,
  `2b` int(5) DEFAULT NULL,
  `3b` int(5) DEFAULT NULL,
  `hr` int(5) DEFAULT NULL,
  `tb` int(5) DEFAULT NULL,
  `hbp` int(5) DEFAULT NULL,
  `bb` int(5) DEFAULT NULL,
  `ibb` int(5) DEFAULT NULL,
  `k` int(5) DEFAULT NULL,
  `sb` int(5) DEFAULT NULL,
  `cs` int(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_Id`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'team_standings'
CREATE TABLE `team_standings` (
  `year` int(11) NOT NULL,
  `team_name` varchar(32) NOT NULL,
  `w` int(11) DEFAULT NULL,
  `l` int(11) DEFAULT NULL,
  `RF` int(11) DEFAULT NULL,
  `RA` int(11) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'teams'
CREATE TABLE `teams` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL,
  `team_name` varchar(32) DEFAULT NULL,
  `team_abb` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
"""

db.query(q)

