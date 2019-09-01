from py_db import db

#Creates MySQL tables for the NSBL database

#This is an initialization script, and only needs to be run once, prior to running every other script


db = db('NSBL')

q = """
-- Create syntax for TABLE '__in_playoff_bracket'
CREATE TABLE `__in_playoff_bracket` (
  `total_playoff_games_played` int(11) DEFAULT NULL,
  `series_id` varchar(16) NOT NULL DEFAULT '',
  `year` int(11) NOT NULL DEFAULT '0',
  `strength_type` varchar(32) NOT NULL DEFAULT '',
  `team` varchar(32) NOT NULL DEFAULT '',
  `opponent` varchar(32) NOT NULL DEFAULT '',
  `series_wins` int(11) NOT NULL DEFAULT '0',
  `series_losses` int(11) NOT NULL DEFAULT '0',
  `team_winProb` decimal(32,3) DEFAULT NULL,
  `team_seriesProb` decimal(32,3) DEFAULT NULL,
  `team_in3` decimal(32,3) DEFAULT NULL,
  `team_in4` decimal(32,3) DEFAULT NULL,
  `team_in5` decimal(32,3) DEFAULT NULL,
  `team_in6` decimal(32,3) DEFAULT NULL,
  `team_in7` decimal(32,3) DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`series_id`,`year`,`strength_type`,`team`,`opponent`,`series_wins`,`series_losses`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '__in_playoff_game_results'
CREATE TABLE `__in_playoff_game_results` (
  `series_id` varchar(16) NOT NULL DEFAULT '',
  `year` int(11) NOT NULL DEFAULT '0',
  `game_num` int(11) NOT NULL DEFAULT '0',
  `teamA` varchar(32) NOT NULL DEFAULT '',
  `teamB` varchar(32) NOT NULL DEFAULT '',
  `winning_team` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`series_id`,`year`,`game_num`,`teamA`,`teamB`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '__in_playoff_probabilities'
CREATE TABLE `__in_playoff_probabilities` (
  `team_name` varchar(32) NOT NULL DEFAULT '',
  `team_abb` varchar(11) DEFAULT NULL,
  `division` varchar(32) DEFAULT NULL,
  `top_seed` decimal(32,3) DEFAULT NULL,
  `win_division` decimal(32,3) DEFAULT NULL,
  `wild_card` decimal(32,3) DEFAULT NULL,
  `year` int(11) NOT NULL DEFAULT '0',
  `total_playoff_games_played` int(11) NOT NULL DEFAULT '0',
  `strength_type` varchar(32) NOT NULL DEFAULT '',
  `strength_pct` decimal(32,3) DEFAULT NULL,
  `win_wc` decimal(32,3) DEFAULT NULL,
  `make_ds` decimal(32,3) DEFAULT NULL,
  `make_cs` decimal(32,3) DEFAULT NULL,
  `make_ws` decimal(32,3) DEFAULT NULL,
  `win_ws` decimal(32,3) DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`team_name`,`year`,`total_playoff_games_played`,`strength_type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '__matchup_matrix'
CREATE TABLE `__matchup_matrix` (
  `team_abb` varchar(32) NOT NULL DEFAULT '',
  `year` int(11) NOT NULL DEFAULT '0',
  `games_played` int(11) NOT NULL DEFAULT '0',
  `opponent` varchar(32) NOT NULL DEFAULT '',
  `strength_type` varchar(32) NOT NULL DEFAULT '',
  `odds_ratio` decimal(32,6) DEFAULT NULL,
  PRIMARY KEY (`team_abb`,`year`,`games_played`,`opponent`,`strength_type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '__optimal_lineups'
CREATE TABLE `__optimal_lineups` (
  `team_abb` varchar(11) NOT NULL DEFAULT '',
  `vs_hand` varchar(11) NOT NULL DEFAULT '',
  `lineup_val` decimal(32,3) NOT NULL DEFAULT '0.000',
  `lineup_var` decimal(32,3) NOT NULL DEFAULT '0.000',
  `c_name` varchar(32) DEFAULT NULL,
  `c_WAR` decimal(32,3) DEFAULT NULL,
  `c_var` decimal(32,3) DEFAULT NULL,
  `1b_name` varchar(32) DEFAULT NULL,
  `1b_WAR` decimal(32,3) DEFAULT NULL,
  `1b_var` decimal(32,3) DEFAULT NULL,
  `2b_name` varchar(32) DEFAULT NULL,
  `2b_WAR` decimal(32,3) DEFAULT NULL,
  `2b_var` decimal(32,3) DEFAULT NULL,
  `3b_name` varchar(32) DEFAULT NULL,
  `3b_WAR` decimal(32,3) DEFAULT NULL,
  `3b_var` decimal(32,3) DEFAULT NULL,
  `ss_name` varchar(32) DEFAULT NULL,
  `ss_WAR` decimal(32,3) DEFAULT NULL,
  `ss_var` decimal(32,3) DEFAULT NULL,
  `lf_name` varchar(32) DEFAULT NULL,
  `lf_WAR` decimal(32,3) DEFAULT NULL,
  `lf_var` decimal(32,3) DEFAULT NULL,
  `cf_name` varchar(32) DEFAULT NULL,
  `cf_WAR` decimal(32,3) DEFAULT NULL,
  `cf_var` decimal(32,3) DEFAULT NULL,
  `rf_name` varchar(32) DEFAULT NULL,
  `rf_WAR` decimal(32,3) DEFAULT NULL,
  `rf_var` decimal(32,3) DEFAULT NULL,
  `dh_name` varchar(32) DEFAULT NULL,
  `dh_WAR` decimal(32,3) DEFAULT NULL,
  `dh_var` decimal(32,3) DEFAULT NULL,
  `lineup_id` varchar(512) NOT NULL DEFAULT '',
  PRIMARY KEY (`team_abb`,`vs_hand`,`lineup_val`,`lineup_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '__optimal_pitching'
CREATE TABLE `__optimal_pitching` (
  `team_abb` varchar(11) NOT NULL DEFAULT '',
  `total_val` decimal(32,3) NOT NULL DEFAULT '0.000',
  `starter_val` decimal(32,3) NOT NULL DEFAULT '0.000',
  `bullpen_val` decimal(32,3) NOT NULL DEFAULT '0.000',
  `total_var` decimal(32,3) DEFAULT NULL,
  `starter_var` decimal(32,3) DEFAULT NULL,
  `bullpen_var` decimal(32,3) DEFAULT NULL,
  `SP1_name` varchar(32) DEFAULT NULL,
  `SP1_WAR` decimal(32,3) DEFAULT NULL,
  `SP1_var` decimal(32,3) DEFAULT NULL,
  `SP2_name` varchar(32) DEFAULT NULL,
  `SP2_WAR` decimal(32,3) DEFAULT NULL,
  `SP2_var` decimal(32,3) DEFAULT NULL,
  `SP3_name` varchar(32) DEFAULT NULL,
  `SP3_WAR` decimal(32,3) DEFAULT NULL,
  `SP3_var` decimal(32,3) DEFAULT NULL,
  `SP4_name` varchar(32) DEFAULT NULL,
  `SP4_WAR` decimal(32,3) DEFAULT NULL,
  `SP4_var` decimal(32,3) DEFAULT NULL,
  `SP5_name` varchar(32) DEFAULT NULL,
  `SP5_WAR` decimal(32,3) DEFAULT NULL,
  `SP5_var` decimal(32,3) DEFAULT NULL,
  `SP6_name` varchar(32) DEFAULT NULL,
  `SP6_WAR` decimal(32,3) DEFAULT NULL,
  `SP6_var` decimal(32,3) DEFAULT NULL,
  `RP1_name` varchar(32) DEFAULT NULL,
  `RP1_WAR` decimal(32,3) DEFAULT NULL,
  `RP1_var` decimal(32,3) DEFAULT NULL,
  `RP2_name` varchar(32) DEFAULT NULL,
  `RP2_WAR` decimal(32,3) DEFAULT NULL,
  `RP2_var` decimal(32,3) DEFAULT NULL,
  `RP3_name` varchar(32) DEFAULT NULL,
  `RP3_WAR` decimal(32,3) DEFAULT NULL,
  `RP3_var` decimal(32,3) DEFAULT NULL,
  `RP4_name` varchar(32) DEFAULT NULL,
  `RP4_WAR` decimal(32,3) DEFAULT NULL,
  `RP4_var` decimal(32,3) DEFAULT NULL,
  `RP5_name` varchar(32) DEFAULT NULL,
  `RP5_WAR` decimal(32,3) DEFAULT NULL,
  `RP5_var` decimal(32,3) DEFAULT NULL,
  `RP6_name` varchar(32) DEFAULT NULL,
  `RP6_WAR` decimal(32,3) DEFAULT NULL,
  `RP6_var` decimal(32,3) DEFAULT NULL,
  `RP7_name` varchar(32) DEFAULT NULL,
  `RP7_WAR` decimal(32,3) DEFAULT NULL,
  `RP7_var` decimal(32,3) DEFAULT NULL,
  `pitching_id` varchar(512) NOT NULL DEFAULT '',
  PRIMARY KEY (`team_abb`,`total_val`,`pitching_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '__playoff_probabilities'
CREATE TABLE `__playoff_probabilities` (
  `team_abb` varchar(11) NOT NULL DEFAULT '',
  `team_name` varchar(32) DEFAULT NULL,
  `year` int(11) NOT NULL DEFAULT '0',
  `games_played` int(11) NOT NULL DEFAULT '0',
  `division` varchar(32) DEFAULT NULL,
  `strength_type` varchar(32) NOT NULL DEFAULT '',
  `strength_pct` decimal(32,3) DEFAULT NULL,
  `var` decimal(32,3) DEFAULT NULL,
  `mean_W` decimal(32,3) DEFAULT NULL,
  `mean_L` decimal(32,3) DEFAULT NULL,
  `p_95` decimal(32,3) DEFAULT NULL,
  `p_75` decimal(32,3) DEFAULT NULL,
  `p_25` decimal(32,3) DEFAULT NULL,
  `p_05` decimal(32,3) DEFAULT NULL,
  `top_seed` decimal(32,8) DEFAULT NULL,
  `win_division` decimal(32,8) DEFAULT NULL,
  `wc_1` decimal(32,8) DEFAULT NULL,
  `wc_2` decimal(32,8) DEFAULT NULL,
  `win_wc` decimal(32,8) DEFAULT NULL,
  `make_ds` decimal(32,8) DEFAULT NULL,
  `make_cs` decimal(32,8) DEFAULT NULL,
  `make_ws` decimal(32,8) DEFAULT NULL,
  `win_ws` decimal(32,8) DEFAULT NULL,
  PRIMARY KEY (`team_abb`,`year`,`games_played`,`strength_type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '__team_strength'
CREATE TABLE `__team_strength` (
  `team_abb` varchar(11) NOT NULL DEFAULT '',
  `team_name` varchar(32) DEFAULT NULL,
  `year` int(11) NOT NULL DEFAULT '0',
  `games_played` int(11) NOT NULL DEFAULT '0',
  `starter_val` decimal(32,3) DEFAULT NULL,
  `bullpen_val` decimal(32,3) DEFAULT NULL,
  `vsR_val` decimal(32,3) DEFAULT NULL,
  `vsL_val` decimal(32,3) DEFAULT NULL,
  `roster_strength` decimal(32,3) DEFAULT NULL,
  `starter_var` decimal(32,3) DEFAULT NULL,
  `bullpen_var` decimal(32,3) DEFAULT NULL,
  `vsR_var` decimal(32,3) DEFAULT NULL,
  `vsL_var` decimal(32,3) DEFAULT NULL,
  `roster_var` decimal(32,3) DEFAULT NULL,
  `overall_var` decimal(32,3) DEFAULT NULL,
  `roster_W` decimal(32,3) DEFAULT NULL,
  `roster_L` decimal(32,3) DEFAULT NULL,
  `roster_pct` decimal(32,3) DEFAULT NULL,
  `current_W` int(11) DEFAULT NULL,
  `current_L` int(11) DEFAULT NULL,
  `current_pct` decimal(32,3) DEFAULT NULL,
  `ros_W` decimal(32,3) DEFAULT NULL,
  `ros_L` decimal(32,3) DEFAULT NULL,
  `ros_pct` decimal(32,3) DEFAULT NULL,
  `projected_W` decimal(32,3) DEFAULT NULL,
  `projected_L` decimal(32,3) DEFAULT NULL,
  `projected_pct` decimal(32,3) DEFAULT NULL,
  PRIMARY KEY (`team_abb`,`year`,`games_played`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '_draft_rosters'
CREATE TABLE `_draft_rosters` (
  `player_name` varchar(50) NOT NULL,
  `fname` varchar(50) DEFAULT NULL,
  `lname` varchar(50) DEFAULT NULL,
  `team_abb` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(50) NOT NULL DEFAULT '',
  `salary` decimal(32,3) NOT NULL,
  `year` varchar(50) NOT NULL DEFAULT '',
  `expires` int(12) NOT NULL DEFAULT '0',
  `opt` varchar(50) NOT NULL DEFAULT '',
  `NTC` varchar(50) DEFAULT NULL,
  `salary_counted` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`player_name`,`salary`,`year`,`expires`,`opt`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '_trade_value'
CREATE TABLE `_trade_value` (
  `year` int(11) DEFAULT NULL,
  `player_name` varchar(50) NOT NULL,
  `fname` varchar(50) DEFAULT NULL,
  `lname` varchar(50) DEFAULT NULL,
  `team_abb` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(50) NOT NULL DEFAULT '',
  `salary` decimal(32,3) NOT NULL,
  `contract_year` varchar(50) NOT NULL DEFAULT '',
  `expires` int(11) NOT NULL DEFAULT '0',
  `opt` varchar(50) NOT NULL DEFAULT '',
  `NTC` varchar(50) DEFAULT NULL,
  `salary_counted` varchar(50) DEFAULT NULL,
  `rl_team` varchar(50) DEFAULT NULL,
  `age` decimal(16,1) DEFAULT '0.0',
  `adj_FV` decimal(16,1) DEFAULT NULL,
  `zWAR` decimal(16,1) DEFAULT NULL,
  `years_remaining` int(11) DEFAULT NULL,
  `est_war_remaining` decimal(16,3) DEFAULT NULL,
  `est_value` decimal(16,3) DEFAULT NULL,
  `est_salary` decimal(16,3) DEFAULT NULL,
  `est_raw_surplus` decimal(16,3) DEFAULT NULL,
  `est_net_present_value` decimal(16,3) DEFAULT NULL,
  PRIMARY KEY (`player_name`,`team_abb`,`position`,`salary`,`expires`,`opt`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE '_trade_value_teams'
CREATE TABLE `_trade_value_teams` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'current_rosters'
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
  `fname` varchar(50) DEFAULT NULL,
  `lname` varchar(50) DEFAULT NULL,
  `team_abb` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(50) NOT NULL DEFAULT '',
  `salary` decimal(32,3) NOT NULL,
  `contract_year` varchar(50) NOT NULL DEFAULT '',
  `expires` int(12) NOT NULL DEFAULT '0',
  `opt` varchar(50) NOT NULL DEFAULT '',
  `NTC` varchar(50) DEFAULT NULL,
  `salary_counted` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`player_name`,`salary`,`contract_year`,`expires`,`opt`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'historical_draft_picks'
CREATE TABLE `historical_draft_picks` (
  `year` int(11) NOT NULL,
  `season` varchar(8) NOT NULL DEFAULT '',
  `overall` int(11) NOT NULL,
  `round` int(11) NOT NULL,
  `pick` int(11) NOT NULL,
  `team_abb` varchar(16) NOT NULL DEFAULT '',
  `player_name` varchar(50) NOT NULL,
  `position` varchar(16) NOT NULL DEFAULT '',
  PRIMARY KEY (`year`,`season`,`overall`,`round`,`pick`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'historical_free_agency'
CREATE TABLE `historical_free_agency` (
  `year` int(11) NOT NULL,
  `day` varchar(32) NOT NULL,
  `player_name` varchar(64) NOT NULL,
  `signing_team` varchar(12) NOT NULL DEFAULT '',
  `rights` varchar(12) NOT NULL DEFAULT '',
  `age` int(12) DEFAULT NULL,
  `position` varchar(12) NOT NULL DEFAULT '',
  `contract_years` int(11) NOT NULL,
  `opt` varchar(12) NOT NULL DEFAULT '',
  `aav` decimal(30,3) NOT NULL,
  `zWAR` decimal(16,1) DEFAULT NULL,
  PRIMARY KEY (`year`,`day`,`signing_team`,`player_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'historical_stats_hitters_advanced'
CREATE TABLE `historical_stats_hitters_advanced` (
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `teams` varchar(128) DEFAULT NULL,
  `end_year` int(11) DEFAULT NULL,
  `start_year` int(11) DEFAULT NULL,
  `years` int(11) NOT NULL DEFAULT '0',
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
  `noD_WAR` decimal(28,2) DEFAULT NULL,
  `WAR` decimal(28,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'historical_stats_hitters_primary'
CREATE TABLE `historical_stats_hitters_primary` (
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `teams` varchar(128) DEFAULT NULL,
  `end_year` int(11) DEFAULT NULL,
  `start_year` int(11) DEFAULT NULL,
  `years` int(11) NOT NULL DEFAULT '0',
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
  `teams` varchar(128) DEFAULT NULL,
  `end_year` int(11) DEFAULT NULL,
  `start_year` int(11) DEFAULT NULL,
  `years` int(11) NOT NULL DEFAULT '0',
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
  `teams` varchar(128) DEFAULT NULL,
  `end_year` int(11) DEFAULT NULL,
  `start_year` int(11) DEFAULT NULL,
  `years` int(11) NOT NULL DEFAULT '0',
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

-- Create syntax for TABLE 'processed_compWAR_defensive'
CREATE TABLE `processed_compWAR_defensive` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `age` int(3) NOT NULL,
  `pa` int(5) DEFAULT NULL,
  `inn` decimal(6,1) DEFAULT NULL,
  `defense` decimal(6,3) DEFAULT NULL,
  `position_adj` decimal(6,3) DEFAULT NULL,
  `dWAR` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_abb`,`player_name`,`position`,`age`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_compWAR_offensive'
CREATE TABLE `processed_compWAR_offensive` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
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
  PRIMARY KEY (`year`,`team_abb`,`player_name`,`position`,`age`)
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

-- Create syntax for TABLE 'processed_team_defense'
CREATE TABLE `processed_team_defense` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `pa` int(5) DEFAULT NULL,
  `inn` decimal(6,1) DEFAULT NULL,
  `defense` decimal(6,3) DEFAULT NULL,
  `position_adj` decimal(6,3) DEFAULT NULL,
  `dWAR` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_team_hitting_advanced'
CREATE TABLE `processed_team_hitting_advanced` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `pa` int(12) DEFAULT NULL,
  `pf` decimal(32,4) DEFAULT NULL,
  `wOBA` decimal(6,4) DEFAULT NULL,
  `park_wOBA` decimal(6,4) DEFAULT NULL,
  `OPS` decimal(6,4) DEFAULT NULL,
  `OPS_plus` decimal(6,2) DEFAULT NULL,
  `babip` decimal(5,3) DEFAULT NULL,
  `wRC` decimal(32,2) DEFAULT NULL,
  `wRC_27` decimal(5,3) DEFAULT NULL,
  `wRC_plus` decimal(6,2) DEFAULT NULL,
  `rAA` decimal(32,2) DEFAULT NULL,
  `oWAR` decimal(32,2) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_team_hitting_basic'
CREATE TABLE `processed_team_hitting_basic` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `avg` decimal(4,3) DEFAULT NULL,
  `obp` decimal(4,3) DEFAULT NULL,
  `slg` decimal(4,3) DEFAULT NULL,
  `pa` int(12) DEFAULT NULL,
  `ab` int(12) DEFAULT NULL,
  `h` int(12) DEFAULT NULL,
  `2b` int(12) DEFAULT NULL,
  `3b` int(12) DEFAULT NULL,
  `hr` int(12) DEFAULT NULL,
  `r` int(12) DEFAULT NULL,
  `rbi` int(12) DEFAULT NULL,
  `hbp` int(12) DEFAULT NULL,
  `bb` int(12) DEFAULT NULL,
  `k` int(12) DEFAULT NULL,
  `sb` int(12) DEFAULT NULL,
  `cs` int(12) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_team_pitching_advanced'
CREATE TABLE `processed_team_pitching_advanced` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
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
  PRIMARY KEY (`year`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_team_pitching_basic'
CREATE TABLE `processed_team_pitching_basic` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `era` decimal(5,2) DEFAULT NULL,
  `w` int(16) DEFAULT NULL,
  `l` int(16) DEFAULT NULL,
  `sv` int(16) DEFAULT NULL,
  `g` int(16) DEFAULT NULL,
  `gs` int(16) DEFAULT NULL,
  `cg` int(16) DEFAULT NULL,
  `sho` int(16) DEFAULT NULL,
  `ip` decimal(32,1) DEFAULT NULL,
  `h` int(16) DEFAULT NULL,
  `r` int(16) DEFAULT NULL,
  `er` int(16) DEFAULT NULL,
  `bb` int(16) DEFAULT NULL,
  `k` int(16) DEFAULT NULL,
  `hr` int(16) DEFAULT NULL,
  `gdp` int(16) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_team_standings_advanced'
CREATE TABLE `processed_team_standings_advanced` (
  `year` int(11) NOT NULL,
  `team_name` varchar(32) NOT NULL DEFAULT '',
  `games_played` int(11) NOT NULL DEFAULT '0',
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
  PRIMARY KEY (`year`,`team_name`,`games_played`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'processed_WAR_hitters'
CREATE TABLE `processed_WAR_hitters` (
  `year` int(11) NOT NULL,
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `position` varchar(5) NOT NULL DEFAULT '',
  `age` int(3) NOT NULL,
  `pa` int(5) DEFAULT NULL,
  `defense` decimal(6,3) DEFAULT NULL,
  `position_adj` decimal(6,3) DEFAULT NULL,
  `dWAR` decimal(5,2) DEFAULT NULL,
  `oWAR` decimal(5,2) DEFAULT NULL,
  `replacement` decimal(6,3) DEFAULT NULL,
  `WAR` decimal(6,3) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_abb`,`player_name`,`position`,`age`)
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

-- Create syntax for TABLE 'ratings_batting'
CREATE TABLE `ratings_batting` (
  `year` int(11) NOT NULL,
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
  PRIMARY KEY (`year`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'ratings_fielding'
CREATE TABLE `ratings_fielding` (
  `year` int(11) NOT NULL,
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
  PRIMARY KEY (`year`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'ratings_pitching'
CREATE TABLE `ratings_pitching` (
  `year` int(11) NOT NULL,
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
  PRIMARY KEY (`year`,`player_name`,`position`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'register_batting_analytical'
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

-- Create syntax for TABLE 'team_standings'
CREATE TABLE `team_standings` (
  `year` int(11) NOT NULL,
  `team_name` varchar(32) NOT NULL,
  `games_played` int(11) NOT NULL DEFAULT '0',
  `w` int(11) DEFAULT NULL,
  `l` int(11) DEFAULT NULL,
  `RF` int(11) DEFAULT NULL,
  `RA` int(11) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_name`,`games_played`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'teams'
CREATE TABLE `teams` (
  `year` int(11) NOT NULL,
  `team_id` int(11) unsigned NOT NULL,
  `team_name` varchar(32) DEFAULT NULL,
  `team_abb` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`year`,`team_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

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

-- Create syntax for TABLE 'zips_fangraphs_batters_counting'
CREATE TABLE `zips_fangraphs_batters_counting` (
  `year` int(11) unsigned NOT NULL,
  `Player` varchar(64) NOT NULL DEFAULT '',
  `team_abb` varchar(8) NOT NULL DEFAULT '',
  `post_date` date DEFAULT NULL,
  `age` int(11) NOT NULL DEFAULT '0',
  `PO` varchar(8) DEFAULT NULL,
  `B` varchar(8) DEFAULT NULL,
  `G` int(11) DEFAULT NULL,
  `AB` int(11) DEFAULT NULL,
  `R` int(11) DEFAULT NULL,
  `H` int(11) DEFAULT NULL,
  `2B` int(11) DEFAULT NULL,
  `3B` int(11) DEFAULT NULL,
  `HR` int(11) DEFAULT NULL,
  `RBI` int(11) DEFAULT NULL,
  `BB` int(11) DEFAULT NULL,
  `SO` int(11) DEFAULT NULL,
  `SB` int(11) DEFAULT NULL,
  `CS` int(11) DEFAULT NULL,
  PRIMARY KEY (`year`,`Player`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_fangraphs_batters_rate'
CREATE TABLE `zips_fangraphs_batters_rate` (
  `year` int(11) unsigned NOT NULL,
  `Player` varchar(64) NOT NULL DEFAULT '',
  `team_abb` varchar(8) NOT NULL DEFAULT '',
  `post_date` date DEFAULT NULL,
  `PA` int(11) DEFAULT NULL,
  `BA` decimal(4,3) DEFAULT NULL,
  `OBP` decimal(4,3) DEFAULT NULL,
  `SLG` decimal(4,3) DEFAULT NULL,
  `OPS_Plus` int(11) DEFAULT NULL,
  `ISO` decimal(4,3) DEFAULT NULL,
  `BABIP` decimal(4,3) DEFAULT NULL,
  `RC_27` decimal(3,1) unsigned zerofill DEFAULT NULL,
  `DEF` int(11) DEFAULT NULL,
  `WAR` decimal(4,1) DEFAULT NULL,
  `Top_Comp` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`year`,`Player`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_fangraphs_pitchers_counting'
CREATE TABLE `zips_fangraphs_pitchers_counting` (
  `year` int(11) unsigned NOT NULL,
  `Player` varchar(64) NOT NULL DEFAULT '',
  `team_abb` varchar(8) NOT NULL DEFAULT '',
  `post_date` date DEFAULT NULL,
  `age` int(11) NOT NULL DEFAULT '0',
  `T` varchar(8) DEFAULT NULL,
  `W` int(11) DEFAULT NULL,
  `L` int(11) DEFAULT NULL,
  `ERA` decimal(4,2) DEFAULT NULL,
  `G` int(11) DEFAULT NULL,
  `GS` int(11) DEFAULT NULL,
  `IP` decimal(4,1) DEFAULT NULL,
  `H` int(11) DEFAULT NULL,
  `ER` int(11) DEFAULT NULL,
  `HR` int(11) DEFAULT NULL,
  `BB` int(11) DEFAULT NULL,
  `SO` int(11) DEFAULT NULL,
  PRIMARY KEY (`year`,`Player`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_fangraphs_pitchers_rate'
CREATE TABLE `zips_fangraphs_pitchers_rate` (
  `year` int(11) unsigned NOT NULL,
  `Player` varchar(64) NOT NULL DEFAULT '',
  `team_abb` varchar(8) NOT NULL DEFAULT '',
  `post_date` date DEFAULT NULL,
  `TBF` int(11) DEFAULT NULL,
  `K_9` decimal(4,2) DEFAULT NULL,
  `BB_9` decimal(4,2) DEFAULT NULL,
  `HR_9` decimal(4,2) DEFAULT NULL,
  `BABIP` decimal(4,3) DEFAULT NULL,
  `ERA_Plus` int(11) DEFAULT NULL,
  `ERA_Minus` int(11) DEFAULT NULL,
  `FIP` decimal(4,2) DEFAULT NULL,
  `WAR` decimal(4,1) DEFAULT NULL,
  `Top_Comp` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`year`,`Player`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_fangraphs_prep_FA_batters'
CREATE TABLE `zips_fangraphs_prep_FA_batters` (
  `year` int(11) unsigned NOT NULL,
  `player_name` varchar(64) NOT NULL DEFAULT '',
  `team_abb` varchar(8) NOT NULL DEFAULT '',
  `pos` varchar(8) DEFAULT NULL,
  `pf` decimal(32,4) DEFAULT NULL,
  `pa` int(11) DEFAULT NULL,
  `ba` decimal(32,3) DEFAULT NULL,
  `obp` decimal(32,3) DEFAULT NULL,
  `slg` decimal(32,3) DEFAULT NULL,
  `zOPS_Plus` int(11) DEFAULT NULL,
  `DEF` int(11) DEFAULT NULL,
  `zWAR` decimal(8,1) DEFAULT NULL,
  `babip` decimal(32,3) DEFAULT NULL,
  `OPS_plus` decimal(32,3) DEFAULT NULL,
  `park_wOBA` decimal(32,3) DEFAULT NULL,
  `wRC_plus` decimal(32,3) DEFAULT NULL,
  `WAR600` decimal(8,1) DEFAULT NULL,
  PRIMARY KEY (`year`,`player_name`,`team_abb`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'zips_fangraphs_prep_FA_pitchers'
CREATE TABLE `zips_fangraphs_prep_FA_pitchers` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `pos` varchar(8) DEFAULT NULL,
  `pf` decimal(32,4) DEFAULT NULL,
  `ip` decimal(30,1) DEFAULT NULL,
  `babip` decimal(34,3) DEFAULT NULL,
  `k_9` decimal(30,3) DEFAULT NULL,
  `bb_9` decimal(30,3) DEFAULT NULL,
  `k_bb` decimal(30,3) DEFAULT NULL,
  `hr_9` decimal(30,3) DEFAULT NULL,
  `zERA_plus` int(11) DEFAULT NULL,
  `zERA_minus` int(11) DEFAULT NULL,
  `zFIP` decimal(30,4) DEFAULT NULL,
  `zWAR` decimal(30,4) DEFAULT NULL,
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

-- Create syntax for TABLE 'zips_offense'
CREATE TABLE `zips_offense` (
  `year` int(11) NOT NULL,
  `player_name` varchar(50) NOT NULL DEFAULT '',
  `team_abb` varchar(5) NOT NULL DEFAULT '',
  `age` int(11) DEFAULT NULL,
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
  `age` int(11) DEFAULT NULL,
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
  `age` int(11) DEFAULT NULL,
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
  `age` int(11) DEFAULT NULL,
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

