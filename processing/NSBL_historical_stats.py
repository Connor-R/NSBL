from py_db import db

# Re-computes historical statistics for all NSBL players, and writes them to the db

db = db('NSBL')

def process():
    print "historical_stats"

    hit_qries = """DROP TABLE IF EXISTS temp;
        CREATE TABLE temp AS
        SELECT o.year
        , COALESCE(CONCAT(nm.right_fname, ' ', nm.right_lname), o.player_name) AS player_name
        , GROUP_CONCAT(DISTINCT hdp.year ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_year
        , GROUP_CONCAT(DISTINCT hdp.season ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_season
        , GROUP_CONCAT(DISTINCT hdp.overall ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_overall
        , GROUP_CONCAT(DISTINCT hdp.round ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_round
        , GROUP_CONCAT(DISTINCT hdp.pick ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_pick_in_round
        , GROUP_CONCAT(DISTINCT hdp.team_abb ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_team
        , cast(group_concat(distinct contract_year) as CHAR(16)) as Contract
        , cast(group_concat(distinct salary) as decimal(10,3)) as Earnings
        , t.team_name as full_team
        , tcf.franchise_name
        , tcf.primary_abb as tcf_team_abb
        , o.position AS listed_position
        , CASE
            WHEN o.year < 2011
                THEN 'unknown'
            WHEN o.year <= 2016 AND o.year >= 2011
                THEN IFNULL(GROUP_CONCAT(DISTINCT sf.pos ORDER BY inn DESC), 'unknown')
            WHEN o.year > 2016
                THEN IFNULL(GROUP_CONCAT(DISTINCT sf.pos ORDER BY inn DESC), 'none')
            END        
        AS def_positions
        , o.age
        , s.pa
        , o.ab
        , o.h
        , o.2b
        , o.3b
        , o.hr
        , o.r
        , o.rbi
        , o.hbp
        , o.bb
        , o.k
        , o.sb
        , o.cs
        , wo.babip
        , ROUND( IF(s.pa = 0, 0, o.bb / s.pa), 3) AS bb_pct
        , ROUND( IF(o.ab = 0, 0, o.k / o.ab), 3) AS k_pct
        , wh.defense
        , wh.position_adj
        , wh.dWAR
        , wo.wOBA
        , wo.OPS_plus
        , wo.wRC_plus
        , wo.rAA
        , wh.oWAR
        , wh.replacement
        , wh.WAR-(wh.defense/10) as noDRS_WAR
        , wh.WAR
        FROM register_batting_primary o
        JOIN register_batting_secondary s USING (year, player_name, team_abb, position, age)
        JOIN processed_compWAR_offensive wo USING (year, player_name, team_abb)
        JOIN processed_WAR_hitters wh USING (year, team_abb, player_name)
        JOIN teams t ON (o.year = t.year AND o.team_abb = t.team_abb)
        JOIN teams_current_franchise tcf ON (t.team_name = tcf.team_name)
        LEFT JOIN statistics_fielding sf ON (o.year = sf.year AND o.player_name = sf.player_name AND t.team_id = sf.team_id)
        LEFT JOIN name_mapper nm ON (1
            AND o.player_name = nm.wrong_name
            AND (nm.start_year IS NULL OR nm.start_year <= o.year)
            AND (nm.end_year IS NULL OR nm.end_year >= o.year)
            AND (nm.position = '' OR nm.position != 'P')
            # AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
            AND (nm.nsbl_team = '' OR nm.nsbl_team = o.team_abb)
        )
        LEFT JOIN name_mapper nm2 ON (nm.right_fname = nm2.right_fname
            AND nm.right_lname = nm2.right_lname
            AND (nm.start_year IS NULL OR nm.start_year = nm2.start_year)
            AND (nm.end_year IS NULL OR nm.end_year = nm2.end_year)
            AND (nm.position = '' OR nm.position = nm2.position)
            AND (nm.rl_team = '' OR nm.rl_team = nm2.rl_team)
        )
        LEFT JOIN yearly_contracts yc ON (nm2.wrong_name = yc.player_name
            and o.year = yc.year
            and if(nm2.wrong_name in ('will smith', 'henry rodriguez', 'luis castillo', 'jose castillo', 'eury perez', 'daniel cabrera', 'alex gonzalez', 'chris young')
                , yc.pos2 = 'h'
                , 1
            )
        )
        LEFT JOIN historical_draft_picks hdp ON ((nm2.wrong_name) = hdp.player_name 
            and o.year >= hdp.year
            and if(nm2.wrong_name in ('will smith', 'henry rodriguez', 'luis castillo', 'jose castillo', 'eury perez', 'daniel cabrera', 'alex gonzalez', 'chris young', 'carlos perez')
                , hdp.position not like "%%p%%"
                , 1
            )
            AND CASE
                WHEN hdp.player_name = 'Josh Bell'
                    THEN hdp.year = 2011
                WHEN hdp.player_name = 'Chris Carter' AND o.year IN (2009, 2010)
                    THEN hdp.year = 2006
                WHEN hdp.player_name = 'Chris Carter' AND o.year >= 2013
                    THEN hdp.year = 2009
                WHEN hdp.player_name = 'Max Muncy'
                    THEN hdp.year = 2013
                ELSE 1
            END
        )
        GROUP BY COALESCE(CONCAT(nm.right_fname, ' ', nm.right_lname), o.player_name), o.year, tcf.franchise_name
        ;

        DROP TABLE IF EXISTS historical_stats_hitters;
        CREATE TABLE historical_stats_hitters AS
        SELECT 'season_by_team' AS group_type
        , IF(MIN(t.year) = MAX(t.year), t.year, CONCAT(MIN(t.year), ' - ', MAX(t.year))) AS year_span
        , COUNT(DISTINCT t.year) AS player_seasons
        , t.player_name
        , GROUP_CONCAT(DISTINCT t.full_team ORDER BY pa DESC SEPARATOR '/') AS team
        , t.listed_position
        , t.def_positions
        , IF(MIN(t.age) = MAX(t.age), t.age, CONCAT(MIN(t.age), ' - ', MAX(t.age))) AS age
        , SUM(t.pa) AS pa
        , SUM(t.ab) AS ab
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.h)/SUM(t.ab)) , 3) AS avg
        , ROUND( IF(SUM(t.pa) = 0, 0, (SUM(t.h)+SUM(t.bb)+SUM(t.hbp))/SUM(t.pa)) , 3) AS obp
        , ROUND( IF(SUM(t.ab) = 0, 0, (SUM(t.h)+SUM(t.2b)+SUM(t.3b)*2+SUM(t.hr)*3)/SUM(t.ab)) , 3) AS slg
        , SUM(t.h) AS h
        , SUM(t.2b) AS 2b
        , SUM(t.3b) AS 3b
        , SUM(t.hr) AS hr
        , SUM(t.r) AS r
        , SUM(t.rbi) AS rbi
        , SUM(t.hbp) AS hbp
        , SUM(t.bb) AS bb
        , SUM(t.k) AS k
        , SUM(t.sb) AS sb
        , SUM(t.cs) AS cs
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.babip*t.pa)/SUM(t.pa)) , 3) AS babip
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.bb)/SUM(t.pa)), 3) AS bb_pct
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.k)/SUM(t.ab)), 3) AS k_pct
        , ROUND( SUM(t.defense) , 1) AS defense
        , ROUND( SUM(t.position_adj) , 1) AS position_adj
        , ROUND( SUM(t.dWAR) , 1) AS dWAR
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.wOBA*t.pa)/SUM(t.pa)) , 3) AS wOBA
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.OPS_plus*t.pa)/SUM(t.pa)) , 0) AS OPS_plus
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.wRC_plus*t.pa)/SUM(t.pa)) , 0) AS wRC_plus
        , ROUND( SUM(t.rAA) , 1) AS rAA
        , ROUND( SUM(t.oWAR) , 1) AS oWAR
        , ROUND( SUM(t.replacement) , 1) AS replacement
        , ROUND( IF(SUM(t.pa) = 0, 0, 600*SUM(t.noDRS_WAR)/SUM(t.pa)), 1) AS noDRS_WAR_600
        , ROUND( IF(SUM(t.pa) = 0, 0, 600*SUM(t.WAR)/SUM(t.pa)), 1) AS WAR_600
        , ROUND( SUM(t.noDRS_WAR) , 1) AS noDRS_WAR
        , ROUND( SUM(t.WAR) , 1) AS WAR
        , t.Draft_Year
        , t.Draft_Season
        , t.Draft_Overall
        , t.Draft_Round
        , t.Draft_Pick_In_Round
        , t.Draft_Team
        , CAST(NULL AS CHAR(16)) AS Contract
        , CAST(NULL AS DECIMAL(10,3)) AS Earnings
        , CAST(NULL AS UNSIGNED) AS Trophy_Count
        , CAST(NULL AS UNSIGNED) AS Black_Ink
        , CAST(NULL AS UNSIGNED) AS Gray_Ink
        , CAST(NULL AS CHAR(100000)) AS Trophy_Details
        FROM temp t
        GROUP BY player_name, listed_position, year, franchise_name
        UNION ALL
        SELECT 'full_season' AS group_type
        , IF(MIN(t.year) = MAX(t.year), t.year, CONCAT(MIN(t.year), ' - ', MAX(t.year))) AS year_span
        , COUNT(DISTINCT t.year) AS player_seasons
        , t.player_name
        , GROUP_CONCAT(DISTINCT t.tcf_team_abb ORDER BY pa DESC SEPARATOR '/') AS team
        , t.listed_position
        , IF(COUNT(t.full_team)=1, t.def_positions, NULL) AS def_positions
        , IF(MIN(t.age) = MAX(t.age), t.age, CONCAT(MIN(t.age), ' - ', MAX(t.age))) AS age
        , SUM(t.pa) AS pa
        , SUM(t.ab) AS ab
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.h)/SUM(t.ab)) , 3) AS avg
        , ROUND( IF(SUM(t.pa) = 0, 0, (SUM(t.h)+SUM(t.bb)+SUM(t.hbp))/SUM(t.pa)) , 3) AS obp
        , ROUND( IF(SUM(t.ab) = 0, 0, (SUM(t.h)+SUM(t.2b)+SUM(t.3b)*2+SUM(t.hr)*3)/SUM(t.ab)) , 3) AS slg
        , SUM(t.h) AS h
        , SUM(t.2b) AS 2b
        , SUM(t.3b) AS 3b
        , SUM(t.hr) AS hr
        , SUM(t.r) AS r
        , SUM(t.rbi) AS rbi
        , SUM(t.hbp) AS hbp
        , SUM(t.bb) AS bb
        , SUM(t.k) AS k
        , SUM(t.sb) AS sb
        , SUM(t.cs) AS cs
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.babip*t.pa)/SUM(t.pa)) , 3) AS babip
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.bb)/SUM(t.pa)), 3) AS bb_pct
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.k)/SUM(t.ab)), 3) AS k_pct
        , ROUND( SUM(t.defense) , 1) AS defense
        , ROUND( SUM(t.position_adj) , 1) AS position_adj
        , ROUND( SUM(t.dWAR) , 1) AS dWAR
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.wOBA*t.pa)/SUM(t.pa)) , 3) AS wOBA
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.OPS_plus*t.pa)/SUM(t.pa)) , 0) AS OPS_plus
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.wRC_plus*t.pa)/SUM(t.pa)) , 0) AS wRC_plus
        , ROUND( SUM(t.rAA) , 1) AS rAA
        , ROUND( SUM(t.oWAR) , 1) AS oWAR
        , ROUND( SUM(t.replacement) , 1) AS replacement
        , ROUND( IF(SUM(t.pa) = 0, 0, 600*SUM(t.noDRS_WAR)/SUM(t.pa)), 1) AS noDRS_WAR_600
        , ROUND( IF(SUM(t.pa) = 0, 0, 600*SUM(t.WAR)/SUM(t.pa)), 1) AS WAR_600
        , ROUND( SUM(t.noDRS_WAR) , 1) AS noDRS_WAR
        , ROUND( SUM(t.WAR) , 1) AS WAR
        , t.Draft_Year
        , t.Draft_Season
        , t.Draft_Overall
        , t.Draft_Round
        , t.Draft_Pick_In_Round
        , t.Draft_Team
        , CAST( (t.Contract) AS CHAR(16)) AS Contract
        , CAST( (t.Earnings) AS DECIMAL(10,3)) AS Earnings
        , CAST(NULL AS UNSIGNED) AS Trophy_Count
        , CAST(NULL AS UNSIGNED) AS Black_Ink
        , CAST(NULL AS UNSIGNED) AS Gray_Ink
        , CAST(NULL AS CHAR(100000)) AS Trophy_Details
        FROM temp t
        GROUP BY player_name, listed_position, year
        UNION ALL
        SELECT 'career_by_team' AS group_type
        , IF(MIN(t.year) = MAX(t.year), t.year, CONCAT(MIN(t.year), ' - ', MAX(t.year))) AS year_span
        , COUNT(DISTINCT t.year) AS player_seasons
        , t.player_name
        , GROUP_CONCAT(DISTINCT t.franchise_name ORDER BY pa DESC SEPARATOR '/') AS team
        , t.listed_position
        , NULL AS def_positions
        , IF(MIN(t.age) = MAX(t.age), t.age, CONCAT(MIN(t.age), ' - ', MAX(t.age))) AS age
        , SUM(t.pa) AS pa
        , SUM(t.ab) AS ab
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.h)/SUM(t.ab)) , 3) AS avg
        , ROUND( IF(SUM(t.pa) = 0, 0, (SUM(t.h)+SUM(t.bb)+SUM(t.hbp))/SUM(t.pa)) , 3) AS obp
        , ROUND( IF(SUM(t.ab) = 0, 0, (SUM(t.h)+SUM(t.2b)+SUM(t.3b)*2+SUM(t.hr)*3)/SUM(t.ab)) , 3) AS slg
        , SUM(t.h) AS h
        , SUM(t.2b) AS 2b
        , SUM(t.3b) AS 3b
        , SUM(t.hr) AS hr
        , SUM(t.r) AS r
        , SUM(t.rbi) AS rbi
        , SUM(t.hbp) AS hbp
        , SUM(t.bb) AS bb
        , SUM(t.k) AS k
        , SUM(t.sb) AS sb
        , SUM(t.cs) AS cs
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.babip*t.pa)/SUM(t.pa)) , 3) AS babip
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.bb)/SUM(t.pa)), 3) AS bb_pct
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.k)/SUM(t.ab)), 3) AS k_pct
        , ROUND( SUM(t.defense) , 1) AS defense
        , ROUND( SUM(t.position_adj) , 1) AS position_adj
        , ROUND( SUM(t.dWAR) , 1) AS dWAR
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.wOBA*t.pa)/SUM(t.pa)) , 3) AS wOBA
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.OPS_plus*t.pa)/SUM(t.pa)) , 0) AS OPS_plus
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.wRC_plus*t.pa)/SUM(t.pa)) , 0) AS wRC_plus
        , ROUND( SUM(t.rAA) , 1) AS rAA
        , ROUND( SUM(t.oWAR) , 1) AS oWAR
        , ROUND( SUM(t.replacement) , 1) AS replacement
        , ROUND( IF(SUM(t.pa) = 0, 0, 600*SUM(t.noDRS_WAR)/SUM(t.pa)), 1) AS noDRS_WAR_600
        , ROUND( IF(SUM(t.pa) = 0, 0, 600*SUM(t.WAR)/SUM(t.pa)), 1) AS WAR_600
        , ROUND( SUM(t.noDRS_WAR) , 1) AS noDRS_WAR
        , ROUND( SUM(t.WAR) , 1) AS WAR
        , t.Draft_Year
        , t.Draft_Season
        , t.Draft_Overall
        , t.Draft_Round
        , t.Draft_Pick_In_Round
        , t.Draft_Team
        , CAST(NULL AS CHAR(16)) AS Contract
        , CAST(NULL AS DECIMAL(10,3)) AS Earnings
        , CAST(NULL AS UNSIGNED) AS Trophy_Count
        , CAST(NULL AS UNSIGNED) AS Black_Ink
        , CAST(NULL AS UNSIGNED) AS Gray_Ink
        , CAST(NULL AS CHAR(100000)) AS Trophy_Details
        FROM temp t
        GROUP BY player_name, franchise_name
        UNION ALL
        SELECT 'full_career' AS group_type
        , IF(MIN(t.year) = MAX(t.year), t.year, CONCAT(MIN(t.year), ' - ', MAX(t.year))) AS year_span
        , COUNT(DISTINCT t.year) AS player_seasons
        , t.player_name
        , GROUP_CONCAT(DISTINCT t.tcf_team_abb ORDER BY year DESC, pa DESC SEPARATOR '/') AS team
        , t.listed_position
        , NULL AS def_positions
        , IF(MIN(t.age) = MAX(t.age), t.age, CONCAT(MIN(t.age), ' - ', MAX(t.age))) AS age
        , SUM(t.pa) AS pa
        , SUM(t.ab) AS ab
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.h)/SUM(t.ab)) , 3) AS avg
        , ROUND( IF(SUM(t.pa) = 0, 0, (SUM(t.h)+SUM(t.bb)+SUM(t.hbp))/SUM(t.pa)) , 3) AS obp
        , ROUND( IF(SUM(t.ab) = 0, 0, (SUM(t.h)+SUM(t.2b)+SUM(t.3b)*2+SUM(t.hr)*3)/SUM(t.ab)) , 3) AS slg
        , SUM(t.h) AS h
        , SUM(t.2b) AS 2b
        , SUM(t.3b) AS 3b
        , SUM(t.hr) AS hr
        , SUM(t.r) AS r
        , SUM(t.rbi) AS rbi
        , SUM(t.hbp) AS hbp
        , SUM(t.bb) AS bb
        , SUM(t.k) AS k
        , SUM(t.sb) AS sb
        , SUM(t.cs) AS cs
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.babip*t.pa)/SUM(t.pa)) , 3) AS babip
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.bb)/SUM(t.pa)), 3) AS bb_pct
        , ROUND( IF(SUM(t.ab) = 0, 0, SUM(t.k)/SUM(t.ab)), 3) AS k_pct
        , ROUND( SUM(t.defense) , 1) AS defense
        , ROUND( SUM(t.position_adj) , 1) AS position_adj
        , ROUND( SUM(t.dWAR) , 1) AS dWAR
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.wOBA*t.pa)/SUM(t.pa)) , 3) AS wOBA
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.OPS_plus*t.pa)/SUM(t.pa)) , 0) AS OPS_plus
        , ROUND( IF(SUM(t.pa) = 0, 0, SUM(t.wRC_plus*t.pa)/SUM(t.pa)) , 0) AS wRC_plus
        , ROUND( SUM(t.rAA) , 1) AS rAA
        , ROUND( SUM(t.oWAR) , 1) AS oWAR
        , ROUND( SUM(t.replacement) , 1) AS replacement
        , ROUND( IF(SUM(t.pa) = 0, 0, 600*SUM(t.noDRS_WAR)/SUM(t.pa)), 1) AS noDRS_WAR_600
        , ROUND( IF(SUM(t.pa) = 0, 0, 600*SUM(t.WAR)/SUM(t.pa)), 1) AS WAR_600
        , ROUND( SUM(t.noDRS_WAR) , 1) AS noDRS_WAR
        , ROUND( SUM(t.WAR) , 1) AS WAR
        , t.Draft_Year
        , t.Draft_Season
        , t.Draft_Overall
        , t.Draft_Round
        , t.Draft_Pick_In_Round
        , t.Draft_Team
        , CAST(NULL AS CHAR(16)) AS Contract
        , CAST(NULL AS DECIMAL(10,3)) AS Earnings
        , CAST(NULL AS UNSIGNED) AS Trophy_Count
        , CAST(NULL AS UNSIGNED) AS Black_Ink
        , CAST(NULL AS UNSIGNED) AS Gray_Ink
        , CAST(NULL AS CHAR(100000)) AS Trophy_Details
        FROM temp t
        GROUP BY player_name
        ;

        ALTER TABLE historical_stats_hitters ADD INDEX `pname_pa_group` (`player_name`, `pa`, `group_type`)
        ;

        ALTER TABLE historical_stats_hitters ADD INDEX `yr_pname_group` (`year_span`, `player_name`, `group_type`)
        ;

        DROP TABLE IF EXISTS temp;
        """

    for qry in hit_qries.split(";")[:-1]:
        db.query(qry)
        db.conn.commit()


    pit_qries = """DROP TABLE IF EXISTS temp;
        CREATE TABLE temp AS
        SELECT o.year
        , COALESCE(CONCAT(nm.right_fname, ' ', nm.right_lname), o.player_name) AS player_name
        , GROUP_CONCAT(DISTINCT hdp.year ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_year
        , GROUP_CONCAT(DISTINCT hdp.season ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_season
        , GROUP_CONCAT(DISTINCT hdp.overall ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_overall
        , GROUP_CONCAT(DISTINCT hdp.round ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_round
        , GROUP_CONCAT(DISTINCT hdp.pick ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_pick_in_round
        , GROUP_CONCAT(DISTINCT hdp.team_abb ORDER BY hdp.year ASC SEPARATOR ' or ') AS draft_team
        , cast(group_concat(distinct contract_year) as CHAR(16)) as Contract
        , cast(group_concat(distinct salary) as decimal(10,3)) as Earnings
        , t.team_name as full_team
        , tcf.franchise_name
        , tcf.primary_abb as tcf_team_abb
        , o.position AS listed_position
        , o.age
        , o.w
        , o.l
        , o.sv
        , o.g
        , o.gs
        , o.cg
        , o.sho
        , o.ip
        , o.h
        , o.r
        , o.er
        , o.bb
        , o.k
        , o.hr
        , o.gdp
        , wp.FIP
        , wp.park_FIP
        , wp.FIP_minus
        , wp.FIP_WAR
        , wp.ERA
        , wp.park_ERA
        , wp.ERA_minus
        , wp.ERA_WAR
        FROM register_pitching_primary o
        JOIN register_pitching_secondary s USING (year, player_name, team_abb, position, age)
        JOIN processed_WAR_pitchers wp USING (year, team_abb, player_name)
        JOIN teams t ON (o.year = t.year AND o.team_abb = t.team_abb)
        JOIN teams_current_franchise tcf ON (t.team_name = tcf.team_name)
        LEFT JOIN name_mapper nm ON (1
            AND o.player_name = nm.wrong_name
            AND (nm.start_year IS NULL OR nm.start_year <= o.year)
            AND (nm.end_year IS NULL OR nm.end_year >= o.year)
            AND (nm.position = '' OR nm.position = 'P')
            # AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
            AND (nm.nsbl_team = '' OR nm.nsbl_team = o.team_abb)
        )
        LEFT JOIN name_mapper nm2 ON (nm.right_fname = nm2.right_fname
            AND nm.right_lname = nm2.right_lname
            AND (nm.start_year IS NULL OR nm.start_year = nm2.start_year)
            AND (nm.end_year IS NULL OR nm.end_year = nm2.end_year)
            AND (nm.position = '' OR nm.position = nm2.position)
            AND (nm.rl_team = '' OR nm.rl_team = nm2.rl_team)
        )
        LEFT JOIN yearly_contracts yc ON (nm2.wrong_name = yc.player_name
            and o.year = yc.year
            and if(nm2.wrong_name in ('will smith', 'henry rodriguez', 'luis castillo', 'jose castillo', 'eury perez', 'daniel cabrera', 'alex gonzalez', 'chris young', 'carlos perez')
                , yc.pos2 = 'p'
                , 1
            )
        )
        LEFT JOIN historical_draft_picks hdp ON ((nm2.wrong_name) = hdp.player_name 
            and o.year >= hdp.year
            and if(nm2.wrong_name in ('will smith', 'henry rodriguez', 'luis castillo', 'jose castillo', 'eury perez', 'daniel cabrera', 'alex gonzalez', 'chris young')
                , hdp.position like "%%p%%"
                , 1
            )
            AND CASE
                WHEN hdp.player_name = 'Cody Reed'
                    THEN hdp.year = 2015
                WHEN hdp.player_name = 'Luis Garcia' 
                    THEN 0
                ELSE 1
            END
        )
        GROUP BY COALESCE(CONCAT(nm.right_fname, ' ', nm.right_lname), o.player_name), o.year, tcf.franchise_name
        ;
        
        DROP TABLE IF EXISTS historical_stats_pitchers;
        CREATE TABLE historical_stats_pitchers AS
        SELECT 'season_by_team' AS group_type
        , IF(MIN(t.year) = MAX(t.year), t.year, CONCAT(MIN(t.year), ' - ', MAX(t.year))) AS year_span
        , COUNT(DISTINCT t.year) AS player_seasons
        , t.player_name
        , GROUP_CONCAT(DISTINCT t.full_team ORDER BY ip DESC SEPARATOR '/') AS team
        , t.listed_position
        , IF(MIN(t.age) = MAX(t.age), t.age, CONCAT(MIN(t.age), ' - ', MAX(t.age))) AS age
        , SUM(t.w) AS w
        , SUM(t.l) AS l
        , SUM(t.sv) AS sv
        , SUM(t.g) AS g
        , SUM(t.gs) AS gs
        , SUM(t.cg) AS cg
        , SUM(t.sho) AS sho
        , ROUND( SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)), 1) AS ip
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.ERA*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS ERA
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.FIP*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS FIP
        , SUM(t.h) AS h
        , SUM(t.r) AS r
        , SUM(t.er) AS er
        , SUM(t.bb) AS bb
        , SUM(t.k) AS k
        , SUM(t.hr) AS hr
        , SUM(t.gdp) AS gdp
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.k)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS k_9
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.bb)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS bb_9
        , ROUND( IF(SUM(t.bb)=0, 0, SUM(t.k)/SUM(t.bb)), 1) AS k_to_bb
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.hr)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS hr_9
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.park_FIP*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS park_FIP
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.FIP_minus*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 0) AS FIP_minus
        , ROUND( SUM(t.FIP_WAR), 1) AS FIP_WAR
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.park_ERA*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS park_ERA
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.ERA_minus*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 0) AS ERA_minus
        , ROUND( SUM(t.ERA_WAR), 1) AS ERA_WAR
        , t.Draft_Year
        , t.Draft_Season
        , t.Draft_Overall
        , t.Draft_Round
        , t.Draft_Pick_In_Round
        , t.Draft_Team
        , CAST(NULL AS CHAR(16)) AS Contract
        , CAST(NULL AS DECIMAL(10,3)) AS Earnings
        , CAST(NULL AS UNSIGNED) AS Trophy_Count
        , CAST(NULL AS UNSIGNED) AS Black_Ink
        , CAST(NULL AS UNSIGNED) AS Gray_Ink
        , CAST(NULL AS CHAR(100000)) AS Trophy_Details
        FROM temp t
        GROUP BY player_name, year, franchise_name
        UNION ALL
        SELECT 'full_season' AS group_type
        , IF(MIN(t.year) = MAX(t.year), t.year, CONCAT(MIN(t.year), ' - ', MAX(t.year))) AS year_span
        , COUNT(DISTINCT t.year) AS player_seasons
        , t.player_name
        , GROUP_CONCAT(DISTINCT t.tcf_team_abb ORDER BY ip DESC SEPARATOR '/') AS team
        , t.listed_position
        , IF(MIN(t.age) = MAX(t.age), t.age, CONCAT(MIN(t.age), ' - ', MAX(t.age))) AS age
        , SUM(t.w) AS w
        , SUM(t.l) AS l
        , SUM(t.sv) AS sv
        , SUM(t.g) AS g
        , SUM(t.gs) AS gs
        , SUM(t.cg) AS cg
        , SUM(t.sho) AS sho
        , ROUND( SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)), 1) AS ip
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.ERA*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS ERA
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.FIP*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS FIP
        , SUM(t.h) AS h
        , SUM(t.r) AS r
        , SUM(t.er) AS er
        , SUM(t.bb) AS bb
        , SUM(t.k) AS k
        , SUM(t.hr) AS hr
        , SUM(t.gdp) AS gdp
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.k)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS k_9
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.bb)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS bb_9
        , ROUND( IF(SUM(t.bb)=0, 0, SUM(t.k)/SUM(t.bb)), 1) AS k_to_bb
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.hr)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS hr_9
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.park_FIP*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS park_FIP
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.FIP_minus*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 0) AS FIP_minus
        , ROUND( SUM(t.FIP_WAR), 1) AS FIP_WAR
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.park_ERA*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS park_ERA
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.ERA_minus*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 0) AS ERA_minus
        , ROUND( SUM(t.ERA_WAR), 1) AS ERA_WAR
        , t.Draft_Year
        , t.Draft_Season
        , t.Draft_Overall
        , t.Draft_Round
        , t.Draft_Pick_In_Round
        , t.Draft_Team
        , CAST( (t.contract) AS CHAR(16)) AS Contract
        , CAST( (t.Earnings) AS DECIMAL(10,3)) AS Earnings
        , CAST(NULL AS UNSIGNED) AS Trophy_Count
        , CAST(NULL AS UNSIGNED) AS Black_Ink
        , CAST(NULL AS UNSIGNED) AS Gray_Ink
        , CAST(NULL AS CHAR(100000)) AS Trophy_Details
        FROM temp t
        GROUP BY player_name, year
        UNION ALL
        SELECT 'career_by_team' AS group_type
        , IF(MIN(t.year) = MAX(t.year), t.year, CONCAT(MIN(t.year), ' - ', MAX(t.year))) AS year_span
        , COUNT(DISTINCT t.year) AS player_seasons
        , t.player_name
        , GROUP_CONCAT(DISTINCT t.full_team ORDER BY ip DESC SEPARATOR '/') AS team
        , t.listed_position
        , IF(MIN(t.age) = MAX(t.age), t.age, CONCAT(MIN(t.age), ' - ', MAX(t.age))) AS age
        , SUM(t.w) AS w
        , SUM(t.l) AS l
        , SUM(t.sv) AS sv
        , SUM(t.g) AS g
        , SUM(t.gs) AS gs
        , SUM(t.cg) AS cg
        , SUM(t.sho) AS sho
        , ROUND( SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)), 1) AS ip
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.ERA*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS ERA
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.FIP*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS FIP
        , SUM(t.h) AS h
        , SUM(t.r) AS r
        , SUM(t.er) AS er
        , SUM(t.bb) AS bb
        , SUM(t.k) AS k
        , SUM(t.hr) AS hr
        , SUM(t.gdp) AS gdp
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.k)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS k_9
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.bb)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS bb_9
        , ROUND( IF(SUM(t.bb)=0, 0, SUM(t.k)/SUM(t.bb)), 1) AS k_to_bb
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.hr)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS hr_9
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.park_FIP*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS park_FIP
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.FIP_minus*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 0) AS FIP_minus
        , ROUND( SUM(t.FIP_WAR), 1) AS FIP_WAR
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.park_ERA*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS park_ERA
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.ERA_minus*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 0) AS ERA_minus
        , ROUND( SUM(t.ERA_WAR), 1) AS ERA_WAR
        , t.Draft_Year
        , t.Draft_Season
        , t.Draft_Overall
        , t.Draft_Round
        , t.Draft_Pick_In_Round
        , t.Draft_Team
        , CAST(NULL AS CHAR(16)) AS Contract
        , CAST(NULL AS DECIMAL(10,3)) AS Earnings
        , CAST(NULL AS UNSIGNED) AS Trophy_Count
        , CAST(NULL AS UNSIGNED) AS Black_Ink
        , CAST(NULL AS UNSIGNED) AS Gray_Ink
        , CAST(NULL AS CHAR(100000)) AS Trophy_Details
        FROM temp t
        GROUP BY player_name, franchise_name
        UNION ALL
        SELECT 'full_career' AS group_type
        , IF(MIN(t.year) = MAX(t.year), t.year, CONCAT(MIN(t.year), ' - ', MAX(t.year))) AS year_span
        , COUNT(DISTINCT t.year) AS player_seasons
        , t.player_name
        , GROUP_CONCAT(DISTINCT t.tcf_team_abb ORDER BY ip DESC SEPARATOR '/') AS team
        , t.listed_position
        , IF(MIN(t.age) = MAX(t.age), t.age, CONCAT(MIN(t.age), ' - ', MAX(t.age))) AS age
        , SUM(t.w) AS w
        , SUM(t.l) AS l
        , SUM(t.sv) AS sv
        , SUM(t.g) AS g
        , SUM(t.gs) AS gs
        , SUM(t.cg) AS cg
        , SUM(t.sho) AS sho
        , ROUND( SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)), 1) AS ip
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.ERA*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS ERA
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.FIP*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS FIP
        , SUM(t.h) AS h
        , SUM(t.r) AS r
        , SUM(t.er) AS er
        , SUM(t.bb) AS bb
        , SUM(t.k) AS k
        , SUM(t.hr) AS hr
        , SUM(t.gdp) AS gdp
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.k)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS k_9
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.bb)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS bb_9
        , ROUND( IF(SUM(t.bb)=0, 0, SUM(t.k)/SUM(t.bb)), 1) AS k_to_bb
        , ROUND( IF(SUM(t.ip)=0, 0, 9*SUM(t.hr)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 1) AS hr_9
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.park_FIP*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS park_FIP
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.FIP_minus*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 0) AS FIP_minus
        , ROUND( SUM(t.FIP_WAR), 1) AS FIP_WAR
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.park_ERA*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 2) AS park_ERA
        , ROUND( IF(SUM(t.ip)=0, 0, SUM(t.ERA_minus*t.ip)/ (SUM(ROUND(t.ip) + (10 * (t.ip - ROUND(t.ip)) / 3)))), 0) AS ERA_minus
        , ROUND( SUM(t.ERA_WAR), 1) AS ERA_WAR
        , t.Draft_Year
        , t.Draft_Season
        , t.Draft_Overall
        , t.Draft_Round
        , t.Draft_Pick_In_Round
        , t.Draft_Team
        , CAST(NULL AS CHAR(16)) AS Contract
        , CAST(NULL AS DECIMAL(10,3)) AS Earnings
        , CAST(NULL AS UNSIGNED) AS Trophy_Count
        , CAST(NULL AS UNSIGNED) AS Black_Ink
        , CAST(NULL AS UNSIGNED) AS Gray_Ink
        , CAST(NULL AS CHAR(100000)) AS Trophy_Details
        FROM temp t
        GROUP BY player_name
        ;

        ALTER TABLE historical_stats_pitchers ADD INDEX `pname_ip_g_group` (`player_name`, `ip`, `g`, `group_type`)
        ;

        ALTER TABLE historical_stats_pitchers ADD INDEX `yr_pname_group` (`year_span`, `player_name`, `group_type`)
        ;

        update historical_stats_hitters h1
        join(
            select h2.player_name
            , sum(h2.Earnings) as total_salary
            from historical_stats_hitters h2
            where 1
                and h2.group_type = 'full_season'
            group by h2.player_name
        ) ts on (h1.player_name = ts.player_name)
        set h1.Earnings = ts.total_salary
        where 1
            and h1.group_type = 'full_career'
        ;

        update historical_stats_pitchers h1
        join(
            select h2.player_name
            , sum(h2.Earnings) as total_salary
            from historical_stats_pitchers h2
            where 1
                and h2.group_type = 'full_season'
            group by h2.player_name
        ) ts on (h1.player_name = ts.player_name)
        set h1.Earnings = ts.total_salary
        where 1
            and h1.group_type = 'full_career'
        ;
        
        DROP TABLE IF EXISTS temp;
        """

    for qry in pit_qries.split(";")[:-1]:
        db.query(qry)
        db.conn.commit()

if __name__ == "__main__":     
    process()

