import argparse
from py_db import db

db = db('NSBL')

def process(year):
    print "NSBL_Draft_FA_HOD"

    print "\thistorical_draft_pick_performance"
    dp_qries ="""
        DROP TABLE IF EXISTS temp;
        CREATE TABLE temp AS
        SELECT IFNULL(CONCAT(nm2.right_fname, ' ', nm2.right_lname), hdp.player_name) AS player_name
        , hdp.year AS draft_year
        , hdp.season AS draft_type
        , tcf.franchise_name
        , hdp.round
        , hdp.pick
        , hdp.overall
        , hdp.position
        , MIN(hfa.year) AS FA
        , nm2.position AS map_position
        FROM historical_draft_picks hdp
        JOIN teams_current_franchise tcf ON (REPLACE(hdp.team_abb, '*', '') = tcf.team_abb)
        LEFT JOIN name_mapper nm ON (1
            AND hdp.player_name = nm.wrong_name
            AND (nm.start_year IS NULL OR nm.start_year <= hdp.year)
            AND (nm.end_year IS NULL OR nm.end_year >= hdp.year)
            AND (nm.position = '' OR IF(nm.position = 'P', hdp.position LIKE "%P%", hdp.position NOT LIKE "%P%"))
            # AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
            AND (nm.nsbl_team = '' OR nm.nsbl_team = tcf.team_abb)
        )
        LEFT JOIN name_mapper nm2 ON (nm.right_fname = nm2.right_fname
            AND nm.right_lname = nm2.right_lname
            AND (nm.start_year IS NULL OR nm.start_year = nm2.start_year)
            AND (nm.end_year IS NULL OR nm.end_year = nm2.end_year)
            AND (nm.position = '' OR nm.position = nm2.position)
            AND (nm.rl_team = '' OR nm.rl_team = nm2.rl_team)
        )
        LEFT JOIN historical_free_agency hfa ON (IFNULL(nm2.wrong_name, hdp.player_name) = hfa.player_name
            AND hfa.year > hdp.year
        )
        GROUP BY hdp.year, IFNULL(CONCAT(nm2.right_fname, ' ', nm2.right_lname), hdp.player_name), hdp.season, hdp.overall
        ; 
        
        DROP TABLE IF EXISTS historical_draft_pick_performance;
        CREATE TABLE historical_draft_pick_performance AS
         SELECT player_name
        , draft_year
        , draft_type
        , drafted_by
        , teams
        , round
        , pick
        , overall
        , position
        , seasons
        , SUM(`WAR/ERA_WAR`) AS `WAR/ERA_WAR`
        , SUM(`noDRS_WAR/FIP_WAR`) AS `noDRS_WAR/FIP_WAR`
        , SUM(`Homegrown_WAR/ERA_WAR`) AS `Homegrown_WAR/ERA_WAR`
        , SUM(`Homegrown_noDRS_WAR/FIP_WAR`) AS `Homegrown_noDRS_WAR/FIP_WAR`
        , MAX(`pa`) AS `PA`
        , MAX(`ab`) AS `AB`
        , MAX(`h`) AS `H`
        , MAX(`hr`) AS `HR`
        , MAX(`sb`) AS `SB`
        , MAX(`avg`) AS `AVG`
        , MAX(`obp`) AS `OBP`
        , MAX(`slg`) AS `SLG`
        , MAX(`ops`) AS `OPS`
        , MAX(`wOBA`) AS `wOBA`
        , MAX(`OPS_plus`) AS `OPS+`
        , MAX(`wRC_plus`) AS `wRC+`
        , MAX(`rAA`) AS `rAA`
        , MAX(`w`) AS `W`
        , MAX(`l`) AS `L`
        , MAX(`sv`) AS `SV`
        , MAX(`g`) AS `G`
        , MAX(`gs`) AS `GS`
        , MAX(`cg`) AS `CG`
        , MAX(`sho`) AS `SHO`
        , MAX(`k`) AS `K`
        , MAX(`ip`) AS `IP`
        , MAX(`ERA`) AS `ERA`
        , MAX(`FIP`) AS `FIP`
        , MAX(`ERA_minus`) AS `ERA_MINUS`
        , MAX(`FIP_minus`) AS `FIP_MINUS`
        FROM(
            SELECT a.player_name
            , a.draft_year
            , a.draft_type
            , a.franchise_name AS drafted_by
            , GROUP_CONCAT(DISTINCT abb.team_abb ORDER BY hh.year_span ASC SEPARATOR '/') AS teams
            , a.round
            , a.pick
            , a.overall
            , a.position    
            , COUNT(DISTINCT hh.year_span) AS seasons
            , ROUND( SUM(hh.WAR) , 1) AS `WAR/ERA_WAR`
            , ROUND( SUM(hh.noDRS_WAR) , 1) AS `noDRS_WAR/FIP_WAR`

            , ROUND( SUM(IF(a.franchise_name = abb.franchise_name AND IF(a.FA IS NULL, 1, hh.year_span < a.FA), hh.WAR, 0)) , 1) AS `Homegrown_WAR/ERA_WAR`
            , ROUND( SUM(IF(a.franchise_name = abb.franchise_name AND IF(a.FA IS NULL, 1, hh.year_span < a.FA), hh.noDRS_WAR, 0)) , 1) AS `Homegrown_noDRS_WAR/FIP_WAR`
                
            , SUM(hh.pa) AS pa
            , SUM(hh.ab) AS ab
            , SUM(hh.h) AS h
            , SUM(hh.hr) AS hr
            , SUM(hh.sb) AS sb
            , ROUND( IF(SUM(hh.ab) = 0, 0, SUM(hh.h)/SUM(hh.ab)) , 3) AS avg
            , ROUND( IF(SUM(hh.pa) = 0, 0, (SUM(hh.h)+SUM(hh.bb)+SUM(hh.hbp))/SUM(hh.pa)) , 3) AS obp
            , ROUND( IF(SUM(hh.ab) = 0, 0, (SUM(hh.h)+SUM(hh.2b)+SUM(hh.3b)*2+SUM(hh.hr)*3)/SUM(hh.ab)) , 3) AS slg
            , ROUND( IF(SUM(hh.pa) = 0 OR SUM(hh.ab) = 0, 0, (SUM(hh.h)+SUM(hh.bb)+SUM(hh.hbp))/SUM(hh.pa))+(SUM(hh.h)+SUM(hh.2b)+SUM(hh.3b)*2+SUM(hh.hr)*3)/SUM(hh.ab), 3) AS ops
            , ROUND( IF(SUM(hh.pa) = 0, 0, SUM(hh.wOBA*hh.pa)/SUM(hh.pa)) , 3) AS wOBA
            , ROUND( IF(SUM(hh.pa) = 0, 0, SUM(hh.OPS_plus*hh.pa)/SUM(hh.pa)) , 0) AS OPS_plus
            , ROUND( IF(SUM(hh.pa) = 0, 0, SUM(hh.wRC_plus*hh.pa)/SUM(hh.pa)) , 0) AS wRC_plus
            , ROUND( SUM(hh.rAA) , 1) AS rAA
            
            , NULL AS w
            , NULL AS l
            , NULL AS sv
            , NULL AS g
            , NULL AS gs
            , NULL AS cg
            , NULL AS sho
            , NULL AS k
            , NULL AS ip
            , NULL AS ERA
            , NULL AS FIP
            , NULL AS ERA_minus
            , NULL AS FIP_minus
            
            
            FROM temp a
            LEFT JOIN historical_stats_hitters hh ON (a.player_name = hh.player_name
                # AND tcf.team_name = hh.team
                # AND IF(a.FA IS NULL, 1, hh.year_span < a.FA)
                AND hh.year_span >= a.draft_year
                AND hh.group_type = 'season_by_team'
                AND IF(0
                , 0, 1)
            )
            LEFT JOIN teams_current_franchise abb ON (hh.team = abb.team_name)
            WHERE 1
                AND (a.map_position IS NULL OR a.map_position = '' OR a.map_position != 'P')
            GROUP BY a.player_name, a.draft_year, a.overall
            HAVING 1
                AND pa IS NOT NULL OR a.position NOT IN ('P', 'RP', 'SP')
            
            UNION ALL
            
            SELECT a.player_name
            , a.draft_year
            , a.draft_type
            , a.franchise_name AS drafted_by
            , GROUP_CONCAT(DISTINCT abb.team_abb ORDER BY hp.year_span ASC SEPARATOR '/') AS teams
            , a.round
            , a.pick
            , a.overall
            , a.position    
            , COUNT(DISTINCT hp.year_span) AS seasons
            , ROUND( SUM(hp.ERA_WAR), 1) AS `WAR/ERA_WAR`
            , ROUND( SUM(hp.FIP_WAR) , 1) AS `noDRS_WAR/FIP_WAR`
            
            , ROUND( SUM(IF(a.franchise_name = abb.franchise_name AND IF(a.FA IS NULL, 1, hp.year_span < a.FA), hp.ERA_WAR, 0)) , 1) AS `Homegrown_WAR/ERA_WAR`
            , ROUND( SUM(IF(a.franchise_name = abb.franchise_name AND IF(a.FA IS NULL, 1, hp.year_span < a.FA), hp.FIP_WAR, 0)) , 1) AS `Homegrown_noDRS_WAR/FIP_WAR`
            
            , NULL AS pa
            , NULL AS ab
            , NULL AS h
            , NULL AS hr
            , NULL AS sb
            , NULL AS avg
            , NULL AS obp
            , NULL AS slg
            , NULL AS ops
            , NULL AS wOBA
            , NULL AS OPS_plus
            , NULL AS wRC_plus
            , NULL AS rAA
            
            , SUM(hp.w) AS w
            , SUM(hp.l) AS l
            , SUM(hp.sv) AS sv
            , SUM(hp.g) AS g
            , SUM(hp.gs) AS gs
            , SUM(hp.cg) AS cg
            , SUM(hp.sho) AS sho
            , SUM(hp.k) AS k
            , ROUND( SUM(hp.ip), 1) AS ip
            , ROUND( IF(SUM(hp.ip)=0, 0, SUM(hp.ERA*hp.ip)/ SUM(hp.ip)), 2) AS ERA
            , ROUND( IF(SUM(hp.ip)=0, 0, SUM(hp.FIP*hp.ip)/ SUM(hp.ip)), 2) AS FIP
            , ROUND( IF(SUM(hp.ip)=0, 0, SUM(hp.ERA_minus*hp.ip)/ SUM(hp.ip)), 0) AS ERA_minus
            , ROUND( IF(SUM(hp.ip)=0, 0, SUM(hp.FIP_minus*hp.ip)/ SUM(hp.ip)), 0) AS FIP_minus
            
            FROM temp a
            LEFT JOIN historical_stats_pitchers hp ON (a.player_name = hp.player_name
                # AND tcf.team_name = hp.team
                # AND IF(a.FA IS NULL, 1, hp.year_span < a.FA)
                AND hp.year_span >= a.draft_year
                AND hp.group_type = 'season_by_team'
                AND IF(0
                    OR(a.player_name = 'Jose Castillo' AND a.draft_year = 2005)
                    OR(a.player_name = 'Josh Fields' AND a.draft_year = 2006)
                    OR(a.player_name = 'Henry Rodriguez' AND draft_year = 2012)
                    OR(a.player_name = 'Will Smith' AND draft_year = 2016)
                , 0, 1)
            )
            LEFT JOIN teams_current_franchise abb ON (hp.team = abb.team_name)
            WHERE 1
                AND (a.map_position IS NULL OR a.map_position = '')
            GROUP BY a.player_name, a.draft_year, a.overall
            HAVING 1
                AND ip IS NOT NULL OR a.position IN ('P', 'RP', 'SP')
        ) a
        GROUP BY a.player_name, a.draft_year, a.draft_type, a.overall
        ORDER BY draft_year ASC, draft_type ASC, overall ASC;

        DROP TABLE IF EXISTS temp;
        """
 
    for qry in dp_qries.split(";")[:-1]:
        db.query(qry)
        db.conn.commit()


    print "\thistorical_free_agent_performance"
    fa_qries = """
        DROP TABLE IF EXISTS temp;
        CREATE TABLE temp AS
        SELECT IFNULL(CONCAT(nm2.right_fname, ' ', nm2.right_lname), hfa.player_name) AS player_name
        , hfa.year AS signing_year
        , tcf.franchise_name
        , hfa.day AS signing_day
        , hfa.rights
        , hfa.contract_years
        , hfa.opt
        , hfa.aav
        , hfa.position
        , MIN(hfa2.year) AS FA
        , nm2.position AS map_position
        FROM historical_free_agency hfa
        JOIN teams_current_franchise tcf ON (REPLACE(hfa.signing_team, '*', '') = tcf.team_abb)
        LEFT JOIN name_mapper nm ON (1
            AND hfa.player_name = nm.wrong_name
            AND (nm.start_year IS NULL OR nm.start_year <= hfa.year)
            AND (nm.end_year IS NULL OR nm.end_year >= hfa.year)
            AND (nm.position = '' OR nm.position != 'P')
            # AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
            AND (nm.nsbl_team = '' OR nm.nsbl_team = tcf.team_abb)
        )
        LEFT JOIN name_mapper nm2 ON (nm.right_fname = nm2.right_fname
            AND nm.right_lname = nm2.right_lname
            AND (nm.start_year IS NULL OR nm.start_year = nm2.start_year)
            AND (nm.end_year IS NULL OR nm.end_year = nm2.end_year)
            AND (nm.position = '' OR nm.position = nm2.position)
            AND (nm.rl_team = '' OR nm.rl_team = nm2.rl_team)
        )
        LEFT JOIN historical_free_agency hfa2 ON (IFNULL(nm2.wrong_name, hfa.player_name) = hfa2.player_name
            AND hfa2.year > hfa.year
        )
        GROUP BY hfa.year, hfa.day, IFNULL(CONCAT(nm2.right_fname, ' ', nm2.right_lname), hfa.player_name), tcf.franchise_name
        ;

        DROP TABLE IF EXISTS historical_free_agent_performance;
        CREATE TABLE historical_free_agent_performance AS
        SELECT player_name
        , signing_year
        , signing_day
        , signed_by
        , teams
        , rights
        , contract_years
        , opt
        , aav
        , position
        , seasons
        , ROUND( IF(seasons>contract_years, seasons, LEAST(%s+1-signing_year,contract_years))*aav, 3) AS `Total_$`
        , homegrown_seasons
        , ROUND( IF(Homegrown_seasons>contract_years, Homegrown_seasons, LEAST(%s+1-signing_year,contract_years-(seasons-Homegrown_seasons)))*aav, 3) AS `Homegrown_$`

        , SUM(`WAR/ERA_WAR`) AS `WAR/ERA_WAR`
        , SUM(`noDRS_WAR/FIP_WAR`) AS `noDRS_WAR/FIP_WAR`

        , SUM(`Homegrown_WAR/ERA_WAR`) AS `Homegrown_WAR/ERA_WAR`
        , SUM(`Homegrown_noDRS_WAR/FIP_WAR`) AS `Homegrown_noDRS_WAR/FIP_WAR`

        , ROUND( 8*SUM(`WAR/ERA_WAR`) - IF(seasons>contract_years, seasons, LEAST(%s+1-signing_year,contract_years))*aav, 3) AS `Surplus_WAR/ERA_WAR`
        , ROUND( 8*SUM(`noDRS_WAR/FIP_WAR`) - IF(seasons>contract_years, seasons, LEAST(%s+1-signing_year,contract_years))*aav, 3) AS `Surplus_noDRS_WAR/FIP_WAR`

        , ROUND( 8*SUM(`Homegrown_WAR/ERA_WAR`) - IF(Homegrown_seasons>contract_years, Homegrown_seasons, LEAST(%s+1-signing_year,contract_years-(seasons-Homegrown_seasons)))*aav, 3) AS `Surplus_Homegrown_WAR/ERA_WAR`
        , ROUND( 8*SUM(`Homegrown_noDRS_WAR/FIP_WAR`) - IF(Homegrown_seasons>contract_years, Homegrown_seasons, LEAST(%s+1-signing_year,contract_years-(seasons-Homegrown_seasons)))*aav, 3) AS `Surplus_Homegrown_noDRS_WAR/FIP_WAR`

        , MAX(`pa`) AS `PA`
        , MAX(`ab`) AS `AB`
        , MAX(`h`) AS `H`
        , MAX(`hr`) AS `HR`
        , MAX(`sb`) AS `SB`
        , MAX(`avg`) AS `AVG`
        , MAX(`obp`) AS `OBP`
        , MAX(`slg`) AS `SLG`
        , MAX(`ops`) AS `OPS`
        , MAX(`wOBA`) AS `wOBA`
        , MAX(`OPS_plus`) AS `OPS+`
        , MAX(`wRC_plus`) AS `wRC+`
        , MAX(`rAA`) AS `rAA`
        , MAX(`w`) AS `W`
        , MAX(`l`) AS `L`
        , MAX(`sv`) AS `SV`
        , MAX(`g`) AS `G`
        , MAX(`gs`) AS `GS`
        , MAX(`cg`) AS `CG`
        , MAX(`sho`) AS `SHO`
        , MAX(`k`) AS `K`
        , MAX(`ip`) AS `IP`
        , MAX(`ERA`) AS `ERA`
        , MAX(`FIP`) AS `FIP`
        , MAX(`ERA_minus`) AS `ERA_MINUS`
        , MAX(`FIP_minus`) AS `FIP_MINUS`
        FROM(
            SELECT a.player_name
            , a.signing_year
            , a.franchise_name AS signed_by
            , GROUP_CONCAT(DISTINCT abb.team_abb ORDER BY hh.year_span ASC SEPARATOR '/') AS teams
            , a.signing_day
            , a.rights
            , a.contract_years
            , a.opt
            , a.aav
            , a.position
            , COUNT(DISTINCT hh.year_span) AS seasons
            , COUNT(DISTINCT IF(a.franchise_name = abb.franchise_name, hh.year_span, NULL)) AS Homegrown_SEASONS
            , ROUND( SUM(hh.WAR) , 1) AS `WAR/ERA_WAR`
            , ROUND( SUM(hh.noDRS_WAR) , 1) AS `noDRS_WAR/FIP_WAR`

            , ROUND( SUM(IF(a.franchise_name = abb.franchise_name, hh.WAR, 0)) , 1) AS `Homegrown_WAR/ERA_WAR`
            , ROUND( SUM(IF(a.franchise_name = abb.franchise_name, hh.noDRS_WAR, 0)) , 1) AS `Homegrown_noDRS_WAR/FIP_WAR`
                
            , SUM(hh.pa) AS pa
            , SUM(hh.ab) AS ab
            , SUM(hh.h) AS h
            , SUM(hh.hr) AS hr
            , SUM(hh.sb) AS sb
            , ROUND( IF(SUM(hh.ab) = 0, 0, SUM(hh.h)/SUM(hh.ab)) , 3) AS avg
            , ROUND( IF(SUM(hh.pa) = 0, 0, (SUM(hh.h)+SUM(hh.bb)+SUM(hh.hbp))/SUM(hh.pa)) , 3) AS obp
            , ROUND( IF(SUM(hh.ab) = 0, 0, (SUM(hh.h)+SUM(hh.2b)+SUM(hh.3b)*2+SUM(hh.hr)*3)/SUM(hh.ab)) , 3) AS slg
            , ROUND( IF(SUM(hh.pa) = 0 OR SUM(hh.ab) = 0, 0, (SUM(hh.h)+SUM(hh.bb)+SUM(hh.hbp))/SUM(hh.pa))+(SUM(hh.h)+SUM(hh.2b)+SUM(hh.3b)*2+SUM(hh.hr)*3)/SUM(hh.ab), 3) AS ops
            , ROUND( IF(SUM(hh.pa) = 0, 0, SUM(hh.wOBA*hh.pa)/SUM(hh.pa)) , 3) AS wOBA
            , ROUND( IF(SUM(hh.pa) = 0, 0, SUM(hh.OPS_plus*hh.pa)/SUM(hh.pa)) , 0) AS OPS_plus
            , ROUND( IF(SUM(hh.pa) = 0, 0, SUM(hh.wRC_plus*hh.pa)/SUM(hh.pa)) , 0) AS wRC_plus
            , ROUND( SUM(hh.rAA) , 1) AS rAA
            
            , NULL AS w
            , NULL AS l
            , NULL AS sv
            , NULL AS g
            , NULL AS gs
            , NULL AS cg
            , NULL AS sho
            , NULL AS k
            , NULL AS ip
            , NULL AS ERA
            , NULL AS FIP
            , NULL AS ERA_minus
            , NULL AS FIP_minus
            
            
            FROM temp a
            LEFT JOIN historical_stats_hitters hh ON (a.player_name = hh.player_name
                # AND tcf.team_name = hh.team
                AND IF(a.FA IS NULL, 1, hh.year_span < a.FA)
                AND hh.year_span < IF(a.opt = 'yes', a.signing_year+a.contract_years+1, a.signing_year+a.contract_years)
                AND hh.year_span >= a.signing_year
                AND hh.group_type = 'season_by_team'
                AND IF(0
                    OR (a.player_name = 'Henry Rodriguez' AND a.signing_year = 2013)
                    OR (a.player_name = 'Matt Reynolds' AND a.signing_year = 2015)
                    OR (a.player_name = 'Matt Duffy' AND a.signing_year = 2016)
                    OR (a.player_name = 'Will Smith' AND a.signing_year = 2018)
                , 0, 1)
            )
            LEFT JOIN teams_current_franchise abb ON (hh.team = abb.team_name)
            WHERE 1
                AND (a.map_position IS NULL OR a.map_position = '' OR a.map_position != 'P')
            GROUP BY a.player_name, a.signing_year, a.signing_day
            HAVING 1
                AND pa IS NOT NULL OR a.position NOT IN ('P', 'RP', 'SP')
            
            UNION ALL
            
            SELECT a.player_name
            , a.signing_year
            , a.franchise_name AS signed_by
            , GROUP_CONCAT(DISTINCT abb.team_abb ORDER BY hp.year_span ASC SEPARATOR '/') AS teams
            , a.signing_day
            , a.rights
            , a.contract_years
            , a.opt
            , a.aav
            , a.position
            , COUNT(DISTINCT hp.year_span) AS seasons
            , COUNT(DISTINCT IF(a.franchise_name = abb.franchise_name, hp.year_span, NULL)) AS Homegrown_SEASONS
            , ROUND( SUM(hp.ERA_WAR), 1) AS `WAR/ERA_WAR`
            , ROUND( SUM(hp.FIP_WAR) , 1) AS `noDRS_WAR/FIP_WAR`
            
            , ROUND( SUM(IF(a.franchise_name = abb.franchise_name, hp.ERA_WAR, 0)) , 1) AS `Homegrown_WAR/ERA_WAR`
            , ROUND( SUM(IF(a.franchise_name = abb.franchise_name, hp.FIP_WAR, 0)) , 1) AS `Homegrown_noDRS_WAR/FIP_WAR`
            
            , NULL AS pa
            , NULL AS ab
            , NULL AS h
            , NULL AS hr
            , NULL AS sb
            , NULL AS avg
            , NULL AS obp
            , NULL AS slg
            , NULL AS ops
            , NULL AS wOBA
            , NULL AS OPS_plus
            , NULL AS wRC_plus
            , NULL AS rAA
            
            , SUM(hp.w) AS w
            , SUM(hp.l) AS l
            , SUM(hp.sv) AS sv
            , SUM(hp.g) AS g
            , SUM(hp.gs) AS gs
            , SUM(hp.cg) AS cg
            , SUM(hp.sho) AS sho
            , SUM(hp.k) AS k
            , ROUND( SUM(hp.ip), 1) AS ip
            , ROUND( IF(SUM(hp.ip)=0, 0, SUM(hp.ERA*hp.ip)/ SUM(hp.ip)), 2) AS ERA
            , ROUND( IF(SUM(hp.ip)=0, 0, SUM(hp.FIP*hp.ip)/ SUM(hp.ip)), 2) AS FIP
            , ROUND( IF(SUM(hp.ip)=0, 0, SUM(hp.ERA_minus*hp.ip)/ SUM(hp.ip)), 0) AS ERA_minus
            , ROUND( IF(SUM(hp.ip)=0, 0, SUM(hp.FIP_minus*hp.ip)/ SUM(hp.ip)), 0) AS FIP_minus
            
            FROM temp a
            LEFT JOIN historical_stats_pitchers hp ON (a.player_name = hp.player_name
                # AND tcf.team_name = hp.team
                AND IF(a.FA IS NULL, 1, hp.year_span < a.FA)
                AND hp.year_span < IF(a.opt = 'yes', a.signing_year+a.contract_years+1, a.signing_year+a.contract_years)
                AND hp.year_span >= a.signing_year
                AND hp.group_type = 'season_by_team'
                AND IF(0
                , 0, 1)
            )
            LEFT JOIN teams_current_franchise abb ON (hp.team = abb.team_name)
            WHERE 1
                AND (a.map_position IS NULL OR a.map_position = '' OR a.map_position = 'P')
            GROUP BY a.player_name, a.signing_year, a.signing_day
            HAVING 1
                AND ip IS NOT NULL OR a.position IN ('P', 'RP', 'SP')
        ) a
        GROUP BY a.player_name, a.signing_year, a.signing_day
        ORDER BY signing_year ASC, signing_day ASC, player_name ASC
        ;

        DROP TABLE IF EXISTS temp;
        """

    fa_qries = fa_qries % (year, year, year, year, year, year)
    for qry in fa_qries.split(";")[:-1]:
        db.query(qry)
        db.conn.commit()


    print "\thistorical_hall_of_fame"
    hof_qries = """
        DROP TABLE IF EXISTS historical_hall_of_fame;
        CREATE TABLE historical_hall_of_fame AS
        SELECT HOF_Class
        , Player_Name
        , Career_Span
        , Total_Seasons
        , Position
        , All_Teams
        , HOF_Team
        , Age_Span

        , SUM(`WAR/ERA_WAR`) AS `WAR/ERA_WAR`
        , SUM(`noDRS_WAR/FIP_WAR`) AS `noDRS_WAR/FIP_WAR`

        , MAX(`pa`) AS `PA`
        , MAX(`ab`) AS `AB`
        , MAX(`h`) AS `H`
        , MAX(`hr`) AS `HR`
        , MAX(`sb`) AS `SB`
        , MAX(`avg`) AS `AVG`
        , MAX(`obp`) AS `OBP`
        , MAX(`slg`) AS `SLG`
        , MAX(`ops`) AS `OPS`
        , MAX(`wOBA`) AS `wOBA`
        , MAX(`OPS_plus`) AS `OPS+`
        , MAX(`wRC_plus`) AS `wRC+`
        , MAX(`rAA`) AS `rAA`
        , MAX(`w`) AS `W`
        , MAX(`l`) AS `L`
        , MAX(`sv`) AS `SV`
        , MAX(`g`) AS `G`
        , MAX(`gs`) AS `GS`
        , MAX(`cg`) AS `CG`
        , MAX(`sho`) AS `SHO`
        , MAX(`k`) AS `K`
        , MAX(`ip`) AS `IP`
        , MAX(`ERA`) AS `ERA`
        , MAX(`FIP`) AS `FIP`
        , MAX(`ERA_minus`) AS `ERA_MINUS`
        , MAX(`FIP_minus`) AS `FIP_MINUS`
        FROM(
            SELECT RIGHT(year_span,4)+2 AS HOF_Class
            , hsh.player_name AS Player_Name
            , year_span AS Career_Span
            , player_seasons AS Total_Seasons
            , listed_position AS Position
            , team AS All_Teams
            , IF(b.MOST_WAR_FRANCHISE=b.MOST_PA_FRANCHISE, b.MOST_WAR_FRANCHISE, CONCAT(b.MOST_WAR_FRANCHISE, ' & ', b.MOST_PA_FRANCHISE)) AS HOF_Team
            , age AS Age_Span
            
            
            , WAR AS `WAR/ERA_WAR`
            , noDRS_WAR AS `noDRS_WAR/FIP_WAR`

            , PA
            , AB
            , H
            , HR
            , SB
            , hsh.AVG
            , OBP
            , SLG
            , OBP+SLG AS OPS
            , wOBA
            , OPS_plus
            , wRC_plus
            , rAA
            
            , NULL AS W
            , NULL AS L
            , NULL AS SV
            , NULL AS G
            , NULL AS GS
            , NULL AS CG
            , NULL AS SHO
            , NULL AS K
            , NULL AS IP
            , NULL AS ERA
            , NULL AS FIP
            , NULL AS ERA_minus
            , NULL AS FIP_minus
            FROM historical_stats_hitters hsh
            JOIN(
                SELECT a.player_name
                , GROUP_CONCAT(DISTINCT war.team) AS MOST_WAR_FRANCHISE
                , GROUP_CONCAT(DISTINCT pa.team) AS MOST_PA_FRANCHISE
                FROM(
                    SELECT hsh.player_name
                    , MAX(WAR) AS WAR
                    , MAX(pa) AS PA
                    FROM historical_stats_hitters hsh
                    WHERE 1
                        AND group_type = 'career_by_team'
                    GROUP BY hsh.player_name
                ) a
                JOIN historical_stats_hitters war ON (a.player_name = war.player_name AND a.WAR = war.WAR)
                JOIN historical_stats_hitters pa ON (a.player_name = pa.player_name AND a.pa = pa.pa)
                WHERE 1
                    AND war.group_type = 'career_by_team'
                    AND pa.group_type = 'career_by_team'
                GROUP BY a.player_name
            ) b ON (hsh.player_name = b.player_name)
            WHERE 1
                AND group_type = 'full_career'
                AND RIGHT(year_span,4) <= 2020-2
                AND (0
                    OR WAR >= 40
                    OR noDRS_WAR >= 40
                    OR HR >= 450
                    OR b.player_name IN ('Barry Bonds', 'Chipper Jones', 'Manny Ramirez', 'David Ortiz'
                    , 'Travis Hafner'
                    )
                )
            
            UNION ALL
            
            SELECT RIGHT(year_span,4)+2 AS HOF_Class
            , hsp.player_name AS Player_Name
            , year_span AS Career_Span
            , player_seasons AS Total_Seasons
            , listed_position AS Position
            , team AS All_Teams
            , IF(b.MOST_WAR_FRANCHISE=b.MOST_IP_FRANCHISE, b.MOST_WAR_FRANCHISE, CONCAT(b.MOST_WAR_FRANCHISE, ' & ', b.MOST_IP_FRANCHISE)) AS HOF_Team
            , age AS Age_Span
            
            , ERA_WAR AS `WAR/ERA_WAR`
            , FIP_WAR AS `noDRS_WAR/FIP_WAR`

            , NULL AS PA
            , NULL AS AB
            , NULL AS H
            , NULL AS HR
            , NULL AS SB
            , NULL AS AVG
            , NULL AS OBP
            , NULL AS SLG
            , NULL AS OPS
            , NULL AS wOBA
            , NULL AS OPS_plus
            , NULL AS wRC_plus
            , NULL AS rAA
            
            , W
            , L
            , SV
            , G
            , GS
            , CG
            , SHO
            , K
            , IP
            , ERA
            , FIP
            , ERA_minus
            , FIP_minus


            FROM historical_stats_pitchers hsp
            JOIN(
                SELECT a.player_name
                , GROUP_CONCAT(DISTINCT war.team) AS MOST_WAR_FRANCHISE
                , GROUP_CONCAT(DISTINCT ip.team) AS MOST_IP_FRANCHISE
                FROM(
                    SELECT hsp.player_name
                    , MAX(FIP_WAR) AS WAR
                    , MAX(ip) AS IP
                    FROM historical_stats_pitchers hsp
                    WHERE 1
                        AND group_type = 'career_by_team'
                    GROUP BY hsp.player_name
                ) a
                JOIN historical_stats_pitchers war ON (a.player_name = war.player_name AND a.WAR = war.FIP_WAR)
                JOIN historical_stats_pitchers ip ON (a.player_name = ip.player_name AND a.ip = ip.ip)
                WHERE 1
                    AND war.group_type = 'career_by_team'
                    AND ip.group_type = 'career_by_team'
                GROUP BY a.player_name
            ) b ON (hsp.player_name = b.player_name)
            WHERE 1
                AND group_type = 'full_career'
                AND RIGHT(year_span,4) <= 2020-2
                AND (0
                    OR FIP_WAR >= 40
                    OR ERA_WAR >= 40
                    OR W >= 200
                    OR SV >= 300
                    OR K >= 2500
                    OR b.player_name IN ('Roy Oswalt', 'Pedro Martinez', 'Randy Johnson', 'Roger Clemens'
                    , 'John Smoltz', 'Mariano Rivera', 'Billy Wagner', 'Joe Nathan', 'Jonathan Papelbon'
                    )
                )
        ) a
        GROUP BY player_name
        ORDER BY HOF_Class, IF(position IN ('cl','sp','rp','mr'), 1, 0);
        """

    for qry in hof_qries.split(";")[:-1]:
        db.query(qry)
        db.conn.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2020)
    args = parser.parse_args()  
    
    process(args.year)