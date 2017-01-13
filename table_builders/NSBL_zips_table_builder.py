from py_db import db

#Creates MySQL tables for importing ZiPS defensive ratings for a given year

#This should be run once before each season (with the correct year value)

db = db('NSBL')


def build():
    query = ""

    for y in range(2017,2018):

        year = str(y)
        print "building " + year + " zips tables"
        q = """
        CREATE TABLE `zips_defense_"""+year+"""` (
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

        CREATE TABLE `zips_offense_"""+year+"""` (
            `year` int(11) NOT NULL,
            `player_name` varchar(50) NOT NULL DEFAULT '',
            `team_abb` varchar(5) NOT NULL DEFAULT '',
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

        CREATE TABLE `zips_pitching_"""+year+"""` (
            `year` int(11) NOT NULL,
            `player_name` varchar(50) NOT NULL DEFAULT '',
            `team_abb` varchar(5) NOT NULL DEFAULT '',
            `w` INT(11) DEFAULT NULL,
            `l` INT(11) DEFAULT NULL,
            `era` decimal(32,2) DEFAULT NULL,
            `g` INT(11) DEFAULT NULL,
            `gs` INT(11) DEFAULT NULL,
            `ip` decimal(32,1) DEFAULT NULL,
            `h` INT(11) DEFAULT NULL,
            `r` INT(11) DEFAULT NULL,
            `er` INT(11) DEFAULT NULL,
            `hr` INT(11) DEFAULT NULL,
            `bb` INT(11) DEFAULT NULL,
            `so` INT(11) DEFAULT NULL,
            `zWAR` decimal(32,1) DEFAULT NULL,
            PRIMARY KEY (`year`,`player_name`, `team_abb`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;


        CREATE TABLE `zips_processed_WAR_hitters_"""+year+"""` (
            `year` int(11) NOT NULL,
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
            PRIMARY KEY (`year`,`player_name`, `team_abb`,`position`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

        CREATE TABLE `zips_processed_WAR_pitchers_"""+year+"""` (
            `year` int(11) NOT NULL,
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
            PRIMARY KEY (`year`,`player_name`, `team_abb`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """

        query = query+q

    db.query(query)


if __name__ == "__main__":        
    build()
