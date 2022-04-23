from py_db import db
from time import time
import argparse

# Fills/updates/modifies the trophies table

db = db('NSBL')

def process(year, backfill):

    prep()

    if backfill.lower() == "true":
        backfill_func(year)

    fill(year)

    leaders(year)

    outliers()

    format_ties(year)

    append_historical_stats()

    tests()


def prep():
    prep_for_prep = """drop table if exists league_hitters
        ;
        create table league_hitters (index idx(year,league,player_name)) as
        select a.*
        , min(rk.year_span) as rookie_year
        from(
            select t.year
            , h.player_name
            , h.age
            , cast(group_concat(distinct left(t.division,2)) AS char(16)) as league
            , group_concat(distinct t.team_name) as teams
            , group_concat(distinct t.team_abb) as team_abbs
            , CASE
                WHEN h.def_positions = 'unknown'
                    THEN h.listed_position
                WHEN h.def_positions is null or h.def_positions = 'none'
                    THEN 'dh'
                WHEN LOCATE(',', h.def_positions) = 0
                    THEN h.def_positions
                ELSE LEFT(h.def_positions,LOCATE(',',h.def_positions) - 1)
            END AS position
            , sum(h.pa) as pa
            , sum(h.ab) as ab
            , format(sum(h.ab*h.avg)/sum(h.ab),3) as avg
            , format(sum(h.pa*h.obp)/sum(h.pa),3) as obp
            , format(sum(h.ab*h.slg)/sum(h.ab),3) as slg
            , sum(h.h) as h
            , sum(h.2b) as 2b
            , sum(h.3b) as 3b
            , sum(h.hr) as hr
            , sum(h.r) as r
            , sum(h.rbi) as rbi
            , sum(h.hbp) as hbp
            , sum(h.bb) as bb
            , sum(h.k) as k
            , sum(h.sb) as sb
            , sum(h.cs) as cs
            , sum(h.defense) as drs
            , sum(h.position_adj) as pos_adj
            , sum(h.dwar) as dWAR
            , round(sum(h.pa*h.ops_plus)/sum(h.pa),0) as ops_plus
            , round(sum(h.pa*h.wrc_plus)/sum(h.pa),0) as wrc_plus
            , sum(h.raa) AS rAA
            , sum(h.owar) as owar
            , sum(h.noDRS_WAR) AS nodrs_war
            , sum(h.war) as war
            from historical_stats_hitters h
            join teams t on (h.year_span = t.year and h.team = t.team_name)
            where h.group_type = 'season_by_team'
            group by h.year_span, h.player_name, h.age, left(t.division,2)
        ) a
        left join historical_stats_hitters rk ON (a.player_name = rk.player_name and rk.pa >= 130 and rk.group_type = 'full_season')
        where 1
        group by a.year, a.player_name, a.age, a.league
        ;
        drop table if exists league_pitchers
        ;
        create table league_pitchers (index idx(year,league,player_name)) as
        select a.*
        , min(rk.year_span) as rookie_year
        from(
            select t.year
            , h.player_name
            , h.age
            , cast(group_concat(distinct left(t.division,2)) as char(16)) as league
            , group_concat(distinct t.team_name) as teams
            , group_concat(distinct t.team_abb) as team_abbs
            , sum(h.w) as w
            , sum(h.l) as l
            , sum(h.sv) as sv
            , sum(h.g) as g
            , sum(h.gs) as gs
            , sum(h.cg) as cg
            , sum(h.sho) as sho
            , sum(h.ip) as ip
            , sum(h.k) as k
            , sum(h.bb) as bb
            , sum(h.hr) as hr
            , sum(h.h) as h
            , sum(h.r) as r
            , sum(h.er) as er
            , sum(h.gdp) as gdp
            , format(9*sum(h.k)/sum(h.ip),1) AS k_9
            , format(9*sum(h.bb)/sum(h.ip),1) AS bb_9
            , format(sum(h.k)/sum(h.bb),1) AS k_to_bb
            , format(sum(h.ip*h.era)/sum(h.ip), 2) as era
            , format(sum(h.ip*h.fip)/sum(h.ip), 2) as fip
            , format(sum(h.ip*h.park_ERA)/sum(h.ip), 2) AS p_era
            , format(sum(h.ip*h.park_FIP)/sum(h.ip), 2) AS p_fip
            , round(sum(h.ip*h.FIP_minus)/sum(h.ip), 0) AS fip_minus
            , round(sum(h.ip*h.ERA_minus)/sum(h.ip), 0) AS era_minus
            , sum(h.FIP_WAR) as fip_war
            , sum(h.era_war) as era_war
            from historical_stats_pitchers h
            join teams t on (h.year_span = t.year and h.team = t.team_name)
            where h.group_type = 'season_by_team'
            group by h.year_span, h.player_name, h.age, left(t.division,2)
        ) a
        left join historical_stats_pitchers rk ON (a.player_name = rk.player_name and (rk.ip >= 50 or rk.g >= 30) and rk.group_type = 'full_season')
        where 1
        group by a.year, a.player_name, a.age, a.league
    ;"""

    print '\tprepping league_ tables'
    for q in prep_for_prep.split(";"):
        if q.strip() != "":
            # print(q)
            db.query(q)
            db.conn.commit()


    mvp_base_query = """drop table if exists %s
        ;
        create table %s as
        select b.*
        from(
            select a.*
            , CASE
                WHEN @yr != year OR @lg != league
                    THEN @rnk := 1
            ELSE @rnk := @rnk+1
            END AS ranking
            , CASE
                WHEN @yr != year OR @lg != league
                    THEN @tie_rnk := 1
                WHEN @prev = a.SCORE
                    THEN @tie_rnk := @tie_rnk
            ELSE @tie_rnk := @rnk
            END AS tie_rank
            , @pos := position as pos_set
            , @lg := league as lg_set
            , @yr := year as yr_set
            , @prev := score as prev_set
            from(
                select year, player_name, league, teams, rookie_year, position
                , (nodrs_war*1.5)+(dWAR*0.5)+(hr*0.02) As score
                , @rnk := 0 as rnk_dummy
                , @pos := '' as pos_dummy
                , @lg := '' as lg_dummy
                , @yr := 0 as yr_dummy
                , @prev := 0.0 as prev_dummy
                , @tie_rnk := 0 as tie_rnk_dummy
                from league_hitters
                where 1
                    %s
                union all
                select year, player_name, league, teams, rookie_year
                , CASE
                    WHEN (((fip_war+era_war)/2)+(w*0.05)+(k*0.005)) > (((fip_war+era_war)/2)+(sv*0.09)+(k*0.005))
                        THEN 'sp'
                    ELSE 'rp'
                END AS position
                , GREATEST(((fip_war+era_war)/2)+(w*0.05)+(k*0.005), ((fip_war+era_war)/2)+(sv*0.09)+(k*0.005)) as score
                , @rnk := 0 as rnk_dummy
                , @pos := '' as pos_dummy
                , @lg := '' as lg_dummy
                , @yr := 0 as yr_dummy
                , @prev := 0.0 as prev_dummy
                , @tie_rnk := 0 as tie_rnk_dummy
                from league_pitchers
                where 1
                    %s
                order by year, league, score desc
            ) a
        ) b
        where b.tie_rank <= %s
        order by year, league, position, ranking
    ;"""

    for vals in [
        ["temp_mvp", "", 50]
        , ["temp_rookie_of_the_year", "and year = rookie_year and year > 2006", 25]
    ]:
        print '\t\t', vals[0]
        query = mvp_base_query % (vals[0], vals[0], vals[1], vals[1], vals[2])
        for q in query.split(";"):
            if q.strip() != "":
                # print(q)
                db.query(q)
                db.conn.commit()


    base_query = """drop table if exists %s #table
        ;
        create table %s as #table
        select b.*
        from(
            select a.*
            , CASE
                %s #rank_bool
                    THEN @rnk := 1
            ELSE @rnk := @rnk+1
            END AS ranking
            , CASE
                %s #rank_bool
                    THEN @tie_rnk := 1
                WHEN @prev = a.SCORE
                    THEN @tie_rnk := @tie_rnk
            ELSE @tie_rnk := @rnk
            END AS tie_rank
            , @pos := position as pos_set
            , @lg := league as lg_set
            , @yr := year as yr_set
            , @prev := score as prev_set
            from(
                select bt.*
                %s #table_add
                , %s as score #score
                , @rnk := 0 as rnk_dummy
                , @pos := '' as pos_dummy
                , @lg := '' as lg_dummy
                , @yr := 0 as yr_dummy
                , @prev := 0.0 as prev_dummy
                , @tie_rnk := 0 as tie_rnk_dummy
                from %s bt #derived_from
                where 1
                    %s #filter
                %s #ordering
            ) a
        ) b
        where b.tie_rank <= %s #limit
    ;"""

    query_details = [
        {"table":"temp_all_star_hitters"
            , "score": "nodrs_war+(dWAR/3)+(hr*0.02)"
            , "derived_from": "league_hitters"
            , "filter": "AND position in ('c', '1b', '2b', '3b', 'ss', 'lf', 'rf', 'cf')"
            , "rank_bool": "WHEN @yr != year OR @lg != league OR @pos != position"
            , "table_add": ", CAST(NULL AS CHAR(8)) as new_position"
            , "ordering": "order by year, league, position, score desc"
            , "limit": 2
            , "other_query": """insert into temp_all_star_hitters
                select b.*
                from(
                    select a.*
                    , CASE
                        WHEN @yr != year OR @lg != league
                            THEN @rnk := 1
                    ELSE @rnk := @rnk+1
                    END AS ranking
                    , CASE
                        WHEN @yr != year OR @lg != league
                            THEN @tie_rnk := 1
                        WHEN @prev = a.SCORE
                            THEN @tie_rnk := @tie_rnk
                    ELSE @tie_rnk := @rnk
                    END AS tie_rank
                    , @pos := position as pos_set
                    , @lg := league as lg_set
                    , @yr := year as yr_set
                    , @prev := score as prev_set
                    from(
                        select h.*
                        , 'dh' as new_position
                        , (h.owar+(h.hr*0.02)) as score
                        , @rnk := 0 as rnk_dummy
                        , @pos := '' as pos_dummy
                        , @lg := '' as lg_dummy
                        , @yr := 0 as yr_dummy
                        , @prev := 0.0 as prev_dummy
                        , @tie_rnk := 0 as tie_rnk_dummy
                        from league_hitters h
                        left join temp_all_star_hitters a on (h.year = a.year and h.league = a.league and h.player_name = a.player_name and h.age = a.age and a.tie_rank <= 2)
                        where 1
                            and a.player_name is null
                        order by year, league, score desc
                    ) a
                ) b
                where b.tie_rank <= 2
                order by year, league, position, ranking;"""
        }
        , {"table": "temp_gold_glove"
            , "score": "defense"
            , "derived_from": "processed_compWAR_defensive bt join teams t using (year, team_abb) #"
            , "filter": "AND year >= 2011 AND position in ('c', '1b', '2b', '3b', 'ss', 'lf', 'rf', 'cf')"
            , "rank_bool": "WHEN @yr != year OR @lg != league OR @pos != position"
            , "table_add": """, left(t.division,2) as league
                , group_concat(distinct t.team_abb) as team_abbs
                , group_concat(distinct t.team_name) as teams"""
            , "ordering": "group by year, league, bt.position, score desc"
            , "limit": 1
            , "other_query": ""
        }
        , {"table": "temp_hank_aaron"
            , "score": "(owar+(hr*0.02))"
            , "derived_from": "league_hitters"
            , "filter": ""
            , "rank_bool": "WHEN @yr != year OR @lg != league"
            , "table_add": ""
            , "ordering": "order by year, league, score desc"
            , "limit": 25
            , "other_query": ""
        }
        , {"table": "temp_silver_slugger"
            , "score": "(wrc_plus + ops_plus + owar)"
            , "derived_from": "league_hitters"
            , "filter": "and pa >= (162*2.5) and position in ('c', '1b', '2b', '3b', 'ss', 'lf', 'rf', 'cf')"
            , "rank_bool": "WHEN @yr != year OR @lg != league OR @pos != position"
            , "table_add": ", CAST(NULL AS CHAR(8)) as new_position"
            , "ordering": "order by year, league, position, score desc"
            , "limit": 1
            , "other_query": """insert into temp_silver_slugger
                select b.*
                from(
                    select a.*
                    , CASE
                        WHEN @yr != year OR @lg != league
                            THEN @rnk := 1
                    ELSE @rnk := @rnk+1
                    END AS ranking
                    , CASE
                        WHEN @yr != year OR @lg != league
                            THEN @tie_rnk := 1
                        WHEN @prev = a.SCORE
                            THEN @tie_rnk := @tie_rnk
                    ELSE @tie_rnk := @rnk
                    END AS tie_rank
                    , @pos := position as pos_set
                    , @lg := league as lg_set
                    , @yr := year as yr_set
                    , @prev := score as prev_set
                    from(
                        select h.*
                        , 'dh' as new_position
                        , (h.wrc_plus + h.ops_plus + h.owar) as score
                        , @rnk := 0 as rnk_dummy
                        , @pos := '' as pos_dummy
                        , @lg := '' as lg_dummy
                        , @yr := 0 as yr_dummy
                        , @prev := 0.0 as prev_dummy
                        , @tie_rnk := 0 as tie_rnk_dummy
                        from league_hitters h
                        left join temp_silver_slugger a on (h.year = a.year and h.league = a.league and h.player_name = a.player_name and h.age = a.age and a.tie_rank <= 1)
                        where 1
                            and h.pa >= (162*2.5)
                            and a.player_name is null
                        order by year, league, score desc
                    ) a
                ) b
                where b.tie_rank <= 1
                order by year, league, position, ranking;"""
        }
        , {"table": "temp_cy_young"
            , "score": "GREATEST(((fip_war+era_war)/2)+(w*0.05)+(k*0.005), ((fip_war+era_war)/2)+(sv*0.09)+(k*0.005))"
            , "derived_from": "league_pitchers"
            , "filter": ""
            , "rank_bool": "WHEN @yr != year OR @lg != league"
            , "table_add": """, CASE
                WHEN (((fip_war+era_war)/2)+(w*0.05)+(k*0.005)) > (((fip_war+era_war)/2)+(sv*0.09)+(k*0.005)) THEN 'sp'
                ELSE 'rp'
                END AS position"""
            , "ordering": "order by year, league, score desc"
            , "limit": 50
            , "other_query": ""
        }
        , {"table": "temp_reliever_of_the_year"
            , "score": "fip_war+era_war+(sv*0.09)+(k*0.005)"
            , "derived_from": "league_pitchers"
            , "filter": "and gs < 5"
            , "rank_bool": "WHEN @yr != year OR @lg != league"
            , "table_add": ", 'rp' as position"
            , "ordering": "order by year, league, score desc"
            , "limit": 50
            , "other_query": ""
        }
        , {"table": "temp_all_star_pitchers"
            , "score": "(fip_war+era_war+(w*0.05)+(k*0.005))"
            , "derived_from": "league_pitchers"
            , "filter": "and ((gs/g) > 0.75)"
            , "rank_bool": "WHEN @yr != year OR @lg != league"
            , "table_add": ", 'sp' as position"
            , "ordering": "order by year, league, score desc"
            , "limit": 9
            , "other_query": """insert into temp_all_star_pitchers
                select b.*
                from(
                    select a.*
                    , CASE
                        WHEN @yr != year OR @lg != league OR @pos != position
                            THEN @rnk := 1
                    ELSE @rnk := @rnk+1
                    END AS ranking
                    , CASE
                        WHEN @yr != year OR @lg != league OR @pos != position
                            THEN @tie_rnk := 1
                        WHEN @prev = a.SCORE
                            THEN @tie_rnk := @tie_rnk
                    ELSE @tie_rnk := @rnk
                    END AS tie_rank
                    , @pos := position as pos_set
                    , @lg := league as lg_set
                    , @yr := year as yr_set
                    , @prev := score as prev_set
                    from(
                        select *
                        , 'rp' as position
                        , fip_war+era_war+(sv*0.09)+(k*0.005) as score
                        , @rnk := 0 as rnk_dummy
                        , @pos := '' as pos_dummy
                        , @lg := '' as lg_dummy
                        , @yr := 0 as yr_dummy
                        , @prev := 0.0 as prev_dummy
                        , @tie_rnk := 0 as tie_rnk_dummy
                        from league_pitchers
                        where gs/g <= 0.25
                        order by year, league, score desc
                    ) a
                ) b
                where b.tie_rank <= 5
                order by year, league, position, ranking;"""
        }
    ]

    for t in query_details:
        print '\t\t', t['table']
        query = base_query % (t['table'], t['table'], t['rank_bool'], t['rank_bool'], t['table_add'], t['score'], t['derived_from'], t['filter'], t['ordering'], t['limit'])
        for q in query.split(";"):
            if q.strip() != "":
                # print(q)
                db.query(q)
                db.conn.commit()
        if t['other_query'] is not None:
            for q in t['other_query'].split(";"):
                if q.strip() != "":
                    # print(q)
                    db.query(q)
                    db.conn.commit()

def backfill_func(year):
    print '\tremoving old backfills'
    q = "delete from trophies where update_type = 'backfilled' and year < %s" % (year)
    # print q
    db.query(q)
    db.conn.commit()

    base_query = """insert into trophies
        select a.*
        from(
            select a.year
            , a.ranking as 'rank_id'
            , '%s' as trophy_name
            , a.league
            , '%s' as trophy_type
            , %s as position
            , a.tie_rank as 'rank'
            , count(distinct a2.player_name) as ties
            , a.score
            , 'backfilled' as update_type
            , NULL as team_name
            , a.player_name
            from %s a
            left join %s a2 on (a.year = a2.year
                and a.league = a2.league
                %s
                and a.tie_rank = a2.tie_rank
                and a.player_name != a2.player_name
            )
            where 1
                %s
                and a.year < %s
            group by year,trophy_name,league,trophy_type,rank,position,player_name
        ) a
        left join trophies t ON (a.year = t.year
            and a.trophy_name = t.trophy_name
            and a.league = t.league
            and (t.update_type = 'manual'
                or if(t.update_type = 'backfilled', if(a.trophy_name = 'All Star', a.position = t.position, 1), 0)
            )
        )
        where 1
            and (t.player_name is null and t.team_name is null)
    ;"""

    query_details = [
        {"trophy_name":"All Star"
            , "trophy_type": "player"
            , "position": "COALESCE(a.new_position, a.position)"
            , "derived_from": "temp_all_star_hitters"
            , "join_filter": "and COALESCE(a.new_position, a.position) = COALESCE(a2.new_position, a2.position)"
            , "rank_filter": "and a.tie_rank <= 2"
        }
        , {"trophy_name":"All Star"
            , "trophy_type": "player"
            , "position": "a.position"
            , "derived_from": "temp_all_star_pitchers"
            , "join_filter": "and a.position = a2.position"
            , "rank_filter": "and if(a.position = 'sp', a.tie_rank <= 9, a.tie_rank <= 5)"
        }
        , {"trophy_name":"Cy Young"
            , "trophy_type": "player"
            , "position": "''"
            , "derived_from": "temp_cy_young"
            , "join_filter": ""
            , "rank_filter": "and a.tie_rank <= 20"
        }
        , {"trophy_name":"Gold Glove"
            , "trophy_type": "player"
            , "position": "a.position"
            , "derived_from": "temp_gold_glove"
            , "join_filter": "and a.position = a2.position"
            , "rank_filter": "and a.tie_rank <= 1"
        }
        , {"trophy_name":"Hank Aaron"
            , "trophy_type": "player"
            , "position": "''"
            , "derived_from": "temp_hank_aaron"
            , "join_filter": ""
            , "rank_filter": "and a.tie_rank <= 10"
        }
        , {"trophy_name":"Most Valuable Player"
            , "trophy_type": "player"
            , "position": "''"
            , "derived_from": "temp_mvp"
            , "join_filter": ""
            , "rank_filter": "and a.tie_rank <= 20"
        }
        , {"trophy_name":"Reliever of the Year"
            , "trophy_type": "player"
            , "position": "''"
            , "derived_from": "temp_reliever_of_the_year"
            , "join_filter": ""
            , "rank_filter": "and a.tie_rank <= 10"
        }
        , {"trophy_name":"Rookie of the Year"
            , "trophy_type": "player"
            , "position": "''"
            , "derived_from": "temp_rookie_of_the_year"
            , "join_filter": ""
            , "rank_filter": "and a.tie_rank <= 10"
        }
        , {"trophy_name":"Silver Slugger"
            , "trophy_type": "player"
            , "position": "COALESCE(a.new_position, a.position)"
            , "derived_from": "temp_silver_slugger"
            , "join_filter": "and COALESCE(a.new_position, a.position) = COALESCE(a2.new_position, a2.position)"
            , "rank_filter": "and a.tie_rank <= 1"
        }
    ]

    for t in query_details:
        print '\t\t', t['derived_from'], '-->', t['trophy_name']
        query = base_query % (t['trophy_name'], t['trophy_type'], t['position'], t['derived_from'], t['derived_from'], t['join_filter'], t['rank_filter'], year)
        for q in query.split(";"):
            if q.strip() != "":
                print(q)
                db.query(q)
                db.conn.commit()

def fill(year):
    print '\tremoving old script'
    q = "delete from trophies where update_type = 'script' and year <= %s" % (year)
    # print q
    db.query(q)
    db.conn.commit()

    print '\t\tadding World Series players'
    q = """INSERT into trophies
        SELECT b.year
        , b.prnk AS `rank_id`
        , 'World Series' AS `trophy_name`
        , '' AS `league`
        , 'player' AS `trophy_type`
        , b.position
        , b.prnk
        , 0 as `ties`
        , 100-b.prnk as `score`
        , 'script' AS `update_type`
        , b.team_name
        , b.player_name
        FROM(
            SELECT a.*
            , IF(@pos = position AND @yr = a.year, @num := @num+1, @num := 1) AS prnk
            , @pos := position AS pos_set
            , @yr := year AS year_set
            FROM(
                SELECT t.year
                , IF(p.gs/p.g > 0.25, 'SP', 'RP') AS position
                , t.team_name
                , p.player_name
                , ROUND((p.FIP_WAR+p.ERA_WAR)/2,1) as WAR
                , @pos := '' AS pos_dummy
                , @yr := 0 AS yr_dummy
                , @num := 0 AS num_dummy
                FROM trophies t
                JOIN teams t2 ON (t.year = t2.year AND t.team_name = t2.team_name)
                JOIN historical_stats_pitchers p ON (t.year = p.year_span AND t.team_name = p.team)
                WHERE 1
                    AND p.group_type = 'season_by_team'
                    AND t.team_name is not null
                    AND t.trophy_name = 'World Series'
                    AND t.trophy_type = 'team'
                UNION ALL
                SELECT t.year
                , CASE
                    WHEN h.def_positions = 'unknown'
                        THEN h.listed_position
                    WHEN LOCATE(',', h.def_positions) = 0
                        THEN h.def_positions
                    ELSE LEFT(h.def_positions,LOCATE(',',h.def_positions) - 1)
                END AS position
                , t.team_name
                , h.player_name
                , h.WAR
                , @pos := '' AS pos_dummy
                , @yr := 0 AS yr_dummy
                , @num := 0 AS num_dummy
                FROM trophies t
                JOIN teams t2 ON (t.year = t2.year AND t.team_name = t2.team_name)
                JOIN historical_stats_hitters h ON (t.year = h.year_span AND t.team_name = h.team)
                WHERE 1
                    AND h.group_type = 'season_by_team'
                    AND t.team_name is not null
                    AND t.trophy_name = 'World Series'
                    AND t.trophy_type = 'team'
                ORDER BY year, position, WAR DESC, player_name
            ) a
            WHERE 1
                AND a.year <= %s
        ) b
    ;""" % (year)
    # print q
    db.query(q)
    db.conn.commit()

    print '\t\tadding Division teams'
    q = """INSERT into trophies
        SELECT b.year
        , b.ranking AS rank_id
        , SUBSTRING_INDEX(b.division,' ',-1) AS trophy_name
        , LEFT(b.division, 2) AS league
        , 'team' AS trophy_type
        , '' AS position
        , b.tie_rank AS rank
        , b.ties_team AS ties
        , b.score
        , 'script' AS update_type
        , b.team_name
        , NULL AS player_name
        FROM(
            SELECT a.*
            , CASE
                WHEN @yr != a.year OR @div != a.division
                    THEN @rnk := 1
            ELSE @rnk := @rnk+1
            END AS ranking
            
            , CASE
                WHEN @yr != a.year OR @div != a.division
                    THEN @tie_rnk := 1
                WHEN @prev = a.SCORE
                    THEN CONCAT(@tie_rnk := @tie_rnk)
            ELSE @tie_rnk := @rnk
            END AS tie_rank
            
            , @yr := a.year AS yr_set
            , @div := a.division AS div_set
            , @prev := a.score AS prev_set
            FROM(
                SELECT ts.*
                , COUNT(DISTINCT ties.team_name) as ties_team
                , ts.w/ts.games_played AS score
                , t.division
                FROM team_standings ts
                JOIN(
                    SELECT year
                    , team_name
                    , MAX(games_played) AS games_played
                    , @yr := 0 AS yr_dummy
                    , @div := '' AS div_dummy
                    , @rnk := 0 AS rnk_dummy
                    , @prev := 0.0 as prev_dummy
                    , @tie_rnk := 0 as tie_rnk_dummy
                    FROM team_standings ts
                    GROUP BY year, team_name
                ) a USING (year, team_name, games_played)
                JOIN teams t ON (ts.year = t.year AND ts.team_name = t.team_name)
                LEFT JOIN(
                    SELECT ts.*
                    , t.division
                    FROM team_standings ts
                    JOIN(
                        SELECT year
                        , team_name
                        , MAX(games_played) AS games_played
                        FROM team_standings ts
                        GROUP BY year, team_name
                    ) a USING (year, team_name, games_played)
                    JOIN teams t ON (ts.year = t.year AND ts.team_name = t.team_name)
                ) ties ON (a.year = ties.year AND t.division = ties.division AND a.team_name != ties.team_name AND (ts.w/ts.games_played) = (ties.w/ties.games_played))
                GROUP BY ts.year, ts.team_name
                ORDER BY year, division, score DESC
            ) a
            WHERE 1
                AND a.year <= %s
        ) b
    ;""" % (year)
    # print q
    db.query(q)
    db.conn.commit()

def leaders(year):
    print '\tremoving old leaders'
    q = "delete from trophies where update_type = 'leaders' and year <= %s" % (year)
    # print q
    db.query(q)
    db.conn.commit()


    base_query = """insert into trophies
        select b.year as year
        , b.ranking as `rank_id`
        , '%s' as trophy_name #t['trophy_name']
        , b.league as league
        , '%s%s' as `trophy_type` #t['trophy_type'], l['trophy_type_add']
        , '' as `position`
        , b.tie_rank as `rank`
        , b.ties
        , b.score as `score`
        , 'leaders' as `update_type`
        , NULL as team_name
        , b.player_name
        from(
            select a.*
            , case
                when %s # l['ranking_bool']
                    then @rnk := 1
            else @rnk := @rnk+1
            end as ranking
            , case
                when %s # l['ranking_bool']
                    then @tie_rnk := 1
                when @prev = a.score
                    then @tie_rnk := @tie_rnk
            else @tie_rnk := @rnk
            end as tie_rank
            , @yr := year as yr_set
            , @lg := league as lg_set
            , @prev := a.score as prev_set
            from(
                select h.*
                %s # l['league_type']
                %s # l['year_rename']
                , NULL as ties
                , round(%s,10) as score # t['score_formula']
                , @yr := 0 as yr_dummy
                , @lg := '' as lg_dummy
                , @prev := 0.0 as prev_dummy
                , @rnk := 0 as rnk_dummy
                , @tie_rnk := 0 as tie_dummy
                from %s_%s h # l['table_type'], t['player_type']
                where 1
                    and h.%s >= (%s*%s) # t['rate'], r['per_g'], l['gp_filter']
                    %s # l['career_filter']
                    %s # l['year_filter']
                group by %s # l['grouping']
                having 1
                    %s # t['score_filter']
                order by %s %s # l['ordering'], t['sort_type']
            ) a
        ) b
    ;"""

    query_details = [
        {"trophy_name":"HITTERS_avg"
            , "trophy_type":"player"
            , "score_formula":"(h.h/h.ab)"
            , "player_type":"hitters"
            , "join_filter":"and (h.h/h.ab) = (ties.h/ties.ab)"
            , "per_g":3
            , "rate":"pa"
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_obp"
            , "trophy_type":"player"
            , "score_formula":"((h.h + h.hbp + h.bb)/(h.pa))"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":3
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_slg"
            , "trophy_type":"player"
            , "score_formula":"((h.h + 2*h.2b + 3*h.hr)/(h.pa))"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":3
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_h"
            , "trophy_type":"player"
            , "score_formula":"(h.h)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_2b"
            , "trophy_type":"player"
            , "score_formula":"(h.2b)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_3b"
            , "trophy_type":"player"
            , "score_formula":"(h.3b)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_hr"
            , "trophy_type":"player"
            , "score_formula":"(h.hr)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_bb"
            , "trophy_type":"player"
            , "score_formula":"(h.bb)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_k"
            , "trophy_type":"player"
            , "score_formula":"(h.k)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_rbi"
            , "trophy_type":"player"
            , "score_formula":"(h.rbi)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_r"
            , "trophy_type":"player"
            , "score_formula":"(h.r)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_sb"
            , "trophy_type":"player"
            , "score_formula":"(h.sb)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"HITTERS_k%"
            , "trophy_type":"player"
            , "score_formula":"(h.k)/(h.ab)"
            , "player_type":"hitters"
            , "rate":"ab"
            , "per_g":3
            , "sort_type":"asc"
            , "score_filter":""
        }
        , {"trophy_name":"HITTERS_bb%"
            , "trophy_type":"player"
            , "score_formula":"(h.bb)/(h.pa)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":3
            , "sort_type":"desc"
            , "score_filter":""
        }
        , {"trophy_name":"HITTERS_ops+"
            , "trophy_type":"player"
            , "score_formula":"(h.ops_plus)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":3
            , "sort_type":"desc"
            , "score_filter":""
        }
        , {"trophy_name":"HITTERS_wrc+"
            , "trophy_type":"player"
            , "score_formula":"(h.wrc_plus)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":3
            , "sort_type":"desc"
            , "score_filter":""
        }
        , {"trophy_name":"HITTERS_raa"
            , "trophy_type":"player"
            , "score_formula":"(h.raa)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":""
        }
        , {"trophy_name":"HITTERS_nodrs_war"
            , "trophy_type":"player"
            , "score_formula":"(h.nodrs_war)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":""
        }
        , {"trophy_name":"HITTERS_war"
            , "trophy_type":"player"
            , "score_formula":"(h.war)"
            , "player_type":"hitters"
            , "rate":"pa"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":""
        }
        , {"trophy_name":"PITCHERS_era"
            , "trophy_type":"player"
            , "score_formula":"27*h.er/(3*floor(h.ip)+floor(mod(h.ip,1)/.3))"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.75
            , "sort_type":"asc"
            , "score_filter":""
        }
        , {"trophy_name":"PITCHERS_fip"
            , "trophy_type":"player"
            , "score_formula":"h.fip"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.75
            , "sort_type":"asc"
            , "score_filter":""
        }
        , {"trophy_name":"PITCHERS_g"
            , "trophy_type":"player"
            , "score_formula":"h.g"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"PITCHERS_w"
            , "trophy_type":"player"
            , "score_formula":"h.w"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"PITCHERS_sv"
            , "trophy_type":"player"
            , "score_formula":"h.sv"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"PITCHERS_cg"
            , "trophy_type":"player"
            , "score_formula":"h.cg"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"PITCHERS_sho"
            , "trophy_type":"player"
            , "score_formula":"h.sho"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"PITCHERS_ip"
            , "trophy_type":"player"
            , "score_formula":"h.ip"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"PITCHERS_k"
            , "trophy_type":"player"
            , "score_formula":"h.k"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"PITCHERS_bb"
            , "trophy_type":"player"
            , "score_formula":"h.bb"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.1
            , "sort_type":"desc"
            , "score_filter":"and score > 0"
        }
        , {"trophy_name":"PITCHERS_k/9"
            , "trophy_type":"player"
            , "score_formula":"27*h.k/(3*floor(h.ip)+floor(mod(h.ip,1)/.3))"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.75
            , "sort_type":"desc"
            , "score_filter":""
        }
        , {"trophy_name":"PITCHERS_bb/9"
            , "trophy_type":"player"
            , "score_formula":"27*h.bb/(3*floor(h.ip)+floor(mod(h.ip,1)/.3))"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.75
            , "sort_type":"asc"
            , "score_filter":""
        }
        , {"trophy_name":"PITCHERS_hr/9"
            , "trophy_type":"player"
            , "score_formula":"27*h.hr/(3*floor(h.ip)+floor(mod(h.ip,1)/.3))"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.75
            , "sort_type":"asc"
            , "score_filter":""
        }
        , {"trophy_name":"PITCHERS_k/bb"
            , "trophy_type":"player"
            , "score_formula":"h.k/h.bb"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.75
            , "sort_type":"desc"
            , "score_filter":""
        }
        , {"trophy_name":"PITCHERS_fip_minus"
            , "trophy_type":"player"
            , "score_formula":"h.fip_minus"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.75
            , "sort_type":"asc"
            , "score_filter":""
        }
        , {"trophy_name":"PITCHERS_era_minus"
            , "trophy_type":"player"
            , "score_formula":"h.fip_minus"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.75
            , "sort_type":"asc"
            , "score_filter":""
        }
        , {"trophy_name":"PITCHERS_fip_war"
            , "trophy_type":"player"
            , "score_formula":"h.fip_war"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.75
            , "sort_type":"desc"
            , "score_filter":""
        }
        , {"trophy_name":"PITCHERS_era_war"
            , "trophy_type":"player"
            , "score_formula":"h.era_war"
            , "player_type":"pitchers"
            , "rate":"ip"
            , "per_g":0.75
            , "sort_type":"desc"
            , "score_filter":""
        }
    ]

    lg_details = [
        {"table_type":"league"
            , "year_rename": ""
            , "trophy_type_add":"_LeagueLeader"
            , "league_type": ""
            , "career_filter":""
            , "year_filter":"and h.year <= %s" % (year)
            , "gp_filter":150
            , "grouping":"h.year, h.league, h.player_name"
            , "ordering":"year, league, score"
            , "ranking_bool":"@yr != year OR @lg != league"
        }
        , {"table_type": "historical_stats"
            , "year_rename": ", h.year_span as year"
            , "trophy_type_add":"_OverallLeader"
            , "league_type": ", '' as league"
            , "career_filter": "and h.group_type = 'full_season'"
            , "year_filter":"and h.year_span <= %s" % (year)
            , "gp_filter":150
            , "grouping":"h.year_span, h.player_name"
            , "ordering":"year, score"
            , "ranking_bool":"@yr != year"
        }
        , {"table_type": "historical_stats"
            , "year_rename": ", h.year_span as year"
            , "trophy_type_add":"_AllTimeSingleSeason"
            , "league_type": ", '' as league"
            , "career_filter": "and h.group_type = 'full_season'"
            , "year_filter":"and h.year_span <= %s" % (year)
            , "gp_filter":150
            , "grouping":"h.year_span, h.player_name"
            , "ordering":"score"
            , "ranking_bool":0
        }
        , {"table_type": "historical_stats"
            , "year_rename": ", 0 as year"
            , "trophy_type_add":"_AllTimeCareer"
            , "league_type": ", '' as league"
            , "career_filter": "and h.group_type = 'full_career'"
            , "year_filter":""
            , "gp_filter":1000
            , "grouping":"h.player_name"
            , "ordering":"score"
            , "ranking_bool":0
        }
    ]

    for t in query_details:
        for l in lg_details:
            print '\t\t', t['trophy_name'], l['trophy_type_add']


            query = base_query % (t['trophy_name']
                , t['trophy_type']
                , l['trophy_type_add']
                , l['ranking_bool']
                , l['ranking_bool']
                , l['league_type']
                , l['year_rename']
                , t['score_formula']
                , l['table_type']
                , t['player_type']
                , t['rate']
                , t['per_g']
                , l['gp_filter']
                , l['career_filter']
                , l['year_filter']
                , l['grouping']
                , t['score_filter']
                , l['ordering']
                , t['sort_type']
            )
            for q in query.split(";"):
                if q.strip() != "":
                    # raw_input(q)
                    db.query(q)
                    db.conn.commit()

def outliers():
    print '\tremoving old outliers'
    q = "delete from trophies where update_type = 'outliers'"
    # print q
    db.query(q)
    db.conn.commit()
    q_dict = {"Triple Crowns":"""insert into trophies
        select b.year
        , b.rank_set as `rank_id`
        , b.new_trophy_name as `trophy_name`
        , b.league
        , b.trophy_type
        , b.position
        , 1 as `rank`
        , 0 as `ties`
        , 0 as `score`
        , 'outliers' AS `update_type`
        , b.team_name
        , b.player_name
        from(
            select a.*
            , IF(@yr = a.year and @lg = a.league AND @tro = a.new_trophy_name, @row := @row+1, @row := 1) as rank_set
            , @yr := a.year as yr_set
            , @lg := a.league as lg_set
            , @tro := a.new_trophy_name AS tro_set
            from(
                select t.*
                , case
                    when trophy_name like "%%HITTERS_%%" then 'HITTERS_tripleCrown'
                    else 'PITCHERS_tripleCrown'
                end as new_trophy_name
                , group_concat(
                    concat(t.trophy_name
                        , ' ('
                        , t.rank
                        , if(t.ties > 0, CONCAT(' tied w/', t.ties, ' others'), '')
                        , ' - '
                        , case
                            when t.trophy_name = 'HITTERS_avg' then format(t.score, 3)
                            when t.trophy_name = 'PITCHERS_era' then format(t.score, 2)
                            else ROUND(t.score,0)
                        end
                        , ')'
                    )
                order by t.rank asc, t.ties asc, t.trophy_name asc separator '\n') as details
                , count(*) as dummy1
                , count(IF(t.rank = 1, t.trophy_name, null)) as dummy2
                , @row := 0 as row_init
                , @yr := 0 as yr_init
                , @lg := '' as lg_init
                , @tro := '' AS tro_init
                from trophies t
                where 1
                    and t.update_type = 'leaders'
                    and t.trophy_type IN ('player_leagueLeader', 'player_overallLeader')
                    and t.trophy_name IN ('HITTERS_avg', 'HITTERS_hr', 'HITTERS_rbi', 'PITCHERS_w', 'PITCHERS_era', 'PITCHERS_k')
                    and t.rank <= 5
                group by t.year, t.player_name, t.league, t.trophy_type
                having 1
                    and dummy1 = 3
                    and dummy2 = 3
                order by year, trophy_name, league
            ) a
        ) b
        ;"""
        , "30-30 seasons": """insert into trophies
        select b.year
        , b.rank_set as `rank_id`
        , 'HITTERS_30/30' as `trophy_name`
        , '' AS `league`
        , 'player' AS `trophy_type`
        , '' AS `position`
        , 1 as `rank`
        , 0 as `ties`
        , 0 as `score`
        , 'outliers' AS `update_type`
        , NULL AS `team_name`
        , b.player_name
        from(
            select a.*
            , IF(@yr = a.year and @lg = a.league, @row := @row+1, @row := 1) as rank_set
            , @yr := a.year as yr_set
            , @lg := a.league as lg_set
            from(
                select t.year
                , t.player_name
                , t.league
                , GROUP_CONCAT(
                    CONCAT(t.trophy_name
                        , ' - '
                        , ROUND(t.score,0)
                    )
                order by t.trophy_name asc separator '\n') as details
                , count(*) as dummy1
                , @row := 0 as row_init
                , @yr := 0 as yr_init
                , @lg := '' as lg_init
                from trophies t
                where 1
                    and t.update_type = 'leaders'
                    and t.trophy_type = 'player_OverallLeader'
                    and t.trophy_name IN ('HITTERS_sb', 'HITTERS_hr')
                    and t.score >= 30
                group by t.year, t.player_name, t.league
                having 1
                    and dummy1 = 2
                ORDER BY year, SUM(t.score) DESC
            ) a
        ) b
        ;"""
    }

    print '\toutliers'
    for desc, query in q_dict.items():
        print '\t\tadding', desc
        for q in query.split(";"):
            if q.strip() != "":
                # raw_input(q)
                db.query(q)
                db.conn.commit()

def format_ties(year):
    print '\tformatting ties in trophies'
    q = """UPDATE trophies t
        JOIN(SELECT t1.*
            , COUNT(*) AS ties_update
            FROM trophies t1
            JOIN trophies t2 ON (t1.trophy_name = t2.trophy_name
                AND t1.league = t2.league
                AND t1.trophy_type = t2.trophy_type
                AND t1.rank = t2.rank
                AND t1.score = t2.score
                AND CASE
                    WHEN t1.trophy_type = 'player_LeagueLeader'
                        THEN t1.player_name != t2.player_name AND t1.year = t2.year AND t1.league = t2.league
                    WHEN t1.trophy_type = 'player_OverallLeader'
                        THEN t1.player_name != t2.player_name AND t1.year = t2.year
                    WHEN t1.trophy_type = 'player_AllTimeSingleSeason'
                        THEN t1.player_name != t2.player_name OR t1.year != t2.year
                    WHEN t1.trophy_type = 'player_AllTimeCareer'
                        THEN t1.player_name != t2.player_name
                END
            )
            WHERE 1
                AND t1.update_type = 'leaders'
                AND t1.ties = 0
                AND t1.year <= %s
            GROUP BY t1.year, t1.rank_id, t1.trophy_name, t1.league, t1.trophy_type, t1.position
        ) b USING (year, rank_id, trophy_name, league, trophy_type, position)
        SET t.ties = b.ties_update
    ;""" % (year)
    # print q
    db.query(q)
    db.conn.commit()

def append_historical_stats():
    print '\tadding trophies to historical_stats'

    db.query("SET SESSION group_concat_max_len = 1000000;")
    db.conn.commit()

    for hp in ('hitters', 'pitchers'):
        print '\t\t', hp

        print '\t\t\tremoving trophy/ink'
        q = "update historical_stats_%s set trophy_count = NULL, black_ink = NULL, gray_ink = NULL, trophy_details = NULL" % (hp)
        # print q
        db.query(q)
        db.conn.commit()

        print '\t\t\tadding seasonal trophies/ink'
        season_q = """update historical_stats_%s h
            join(
                select a.year
                , a.player_name
                , a.h_team
                , a.p_team
                , count(distinct if(a.new_trophy_type = 'award'
                    and a.trophy_name != 'World Series'
                    and a.update_type != 'outliers'
                    and (a.rank = 1 or a.trophy_name = 'all star')
                , a.trophy_name, null)) as trophy_count
                , count(distinct if(a.trophy_type = 'player_leagueleader' and a.rank = 1, a.trophy_name, null)) as black_ink
                , count(distinct if(a.trophy_type = 'player_leagueleader' and a.rank <= 10, a.trophy_name, null)) as gray_ink
                , group_concat(concat('- '
                    , if(a.new_trophy_type != 'Award', concat(a.new_trophy_type, ' '), '')
                    , if(a.update_type = 'outliers' or a.trophy_name in ('World Series', 'All Star', 'Gold Glove', 'Silver Slugger') or (a.new_trophy_type = 'award' and a.rank = 1 and a.ties = 0) 
                        , upper(a.new_trophy_name)
                        , concat(if(a.new_trophy_type = 'award' and a.rank = 1, upper(a.new_trophy_name), a.new_trophy_name)
                            , ' ('
                            , if(a.ties > 0, 'T-', '')
                            , a.rank
                            , if(a.ties > 0, concat(' w/', a.ties, ' others'), '')
                            , ')'
                            )
                        )
                    )
                order by if(a.trophy_name = 'World Series', 1, 0) desc
                , if(a.update_type = 'outliers', 1, 0) desc
                , if(a.trophy_name in ('All Star', 'Gold Glove', 'Silver Slugger'), 1, 0) desc
                , (case
                    when a.trophy_type = 'player' then 0
                    when a.trophy_type = 'player_alltimesingleseason' then 1
                    when a.trophy_type = 'player_overallleader' then 2
                    when a.trophy_type = 'player_leagueleader' then 3
                end) asc, a.rank asc, a.rank_id asc, a.new_trophy_name asc
                separator ' \n') as trophy_details
                from(
                    select t.*
                    , case when t.trophy_type = 'player' then 'Award'
                        when t.trophy_type = 'player_alltimesingleseason' then 'All-Time Single Season'
                        when t.trophy_type = 'player_overallleader' then 'Overall'
                        when t.trophy_type = 'player_leagueleader' then t.league
                    end as new_trophy_type
                    , case
                        when t.trophy_type = 'player'
                            then (replace(replace(replace(replace(t.trophy_name, 'HITTERS_', ''), 'PITCHERS_', ''), '_plus', '+'), '_minus', '-'))
                        else upper(replace(replace(replace(replace(t.trophy_name, 'HITTERS_', ''), 'PITCHERS_', ''), '_plus', '+'), '_minus', '-'))
                    end as new_trophy_name
                    , group_concat(distinct h.team) AS h_team
                    , group_concat(distinct p.team) AS p_team
                    from trophies t
                    left join historical_stats_hitters h on (t.year = h.year_span
                        and t.player_name = h.player_name
                        and h.group_type = 'full_season'
                        and if(t.trophy_type != 'player', LEFT(t.trophy_name,1) = 'H', 1)
                    )
                    left join historical_stats_pitchers p on (t.year = p.year_span
                        and t.player_name = p.player_name
                        and p.group_type = 'full_season'
                        and if(t.trophy_type != 'player', LEFT(t.trophy_name,1) = 'P', 1)
                    )
                    where 1
                        and t.player_name is not null
                        and t.trophy_type in ('player', 'player_alltimesingleseason', 'player_overallleader', 'player_leagueleader')
                        and case
                            when t.trophy_type = 'player_alltimesingleseason' then t.rank <= 20
                            when t.trophy_type = 'player_overallleader' then t.rank <= 10
                            when t.trophy_type = 'player_leagueleader' then t.rank <= 10
                        else 1
                        end
                    group by t.year, t.trophy_name, t.league, t.trophy_type, t.rank, t.player_name
                ) a
                group by year, player_name, h_team, p_team
                order by trophy_count desc, black_ink desc, gray_ink desc, year desc
            ) t on (h.player_name = t.player_name and h.year_span = t.year and h.team = t.%s_team)
            set h.trophy_count = t.trophy_count
            , h.black_ink = t.black_ink
            , h.gray_ink = t.gray_ink
            , h.trophy_details = t.trophy_details
            where 1
                and h.group_type  = 'full_season'
        ;""" % (hp, hp[0])
        # print season_q
        db.query(season_q)
        db.conn.commit()

        print '\t\t\tadding career trophies/ink'
        career_queries = """drop table if exists temp;
            create table temp as
            select t.*
            , case when t.trophy_type = 'player' then 'Award'
                when t.trophy_type = 'player_alltimesingleseason' then 'All-Time Single Season'
                when t.trophy_type = 'player_overallleader' then 'Overall'
                when t.trophy_type = 'player_AllTimeCareer' then 'Career'
                when t.trophy_type = 'player_leagueleader' then t.league
            end as new_trophy_type
            , case
                when t.trophy_type = 'player'
                    then (replace(replace(replace(replace(t.trophy_name, 'HITTERS_', ''), 'PITCHERS_', ''), '_plus', '+'), '_minus', '-'))
                else upper(replace(replace(replace(replace(t.trophy_name, 'HITTERS_', ''), 'PITCHERS_', ''), '_plus', '+'), '_minus', '-'))
            end as new_trophy_name
            , group_concat(distinct h.year_span) AS h_years
            , group_concat(distinct p.year_span) AS p_years
            , group_concat(distinct h.team) AS h_team
            , group_concat(distinct p.team) AS p_team
            from trophies t
            left join historical_stats_hitters h on (t.player_name = h.player_name
                and h.group_type = 'full_career'
                and if(t.trophy_type != 'player', LEFT(t.trophy_name,1) = 'H', 1)
            )
            left join historical_stats_pitchers p on (t.player_name = p.player_name
                and p.group_type = 'full_career'
                and if(t.trophy_type != 'player', LEFT(t.trophy_name,1) = 'P', 1)
            )
            where 1
                and t.player_name is not null
                and t.trophy_type in ('player', 'player_alltimesingleseason', 'player_overallleader', 'player_leagueleader', 'player_AllTimeCareer')
                and case
                    when t.trophy_type = 'player_alltimesingleseason' then t.rank <= 10
                    when t.trophy_type = 'player_overallleader' then t.rank <= 10
                    when t.trophy_type = 'player_leagueleader' then t.rank <= 10
                    when t.trophy_type = 'player_AllTimeCareer' then t.rank <= 20
                else 1
                end
            group by t.year, t.trophy_name, t.league, t.trophy_type, t.rank, t.player_name
            ;


            update historical_stats_%s h
            join(
                select a.player_name
                , a.h_years
                , a.p_years
                , a.h_team
                , a.p_team
                , count(distinct if(a.new_trophy_type = 'award'
                    and a.trophy_name != 'World Series'
                    and a.update_type != 'outliers'
                    and (a.rank = 1 or a.trophy_name = 'all star')
                , concat(a.trophy_name, a.year), null)) as trophy_count
                , count(distinct if(a.trophy_type = 'player_leagueleader' and a.rank = 1, concat(a.trophy_name, a.year), null)) as black_ink
                , count(distinct if(a.trophy_type = 'player_leagueleader' and a.rank <= 10, concat(a.trophy_name, a.year), null)) as gray_ink
                , concat(c.accolades
                    , if(c.accolades is null, '', ' \n')
                    , ifnull(group_concat(if((a.trophy_type = 'player_alltimesingleseason' and a.rank <= 1) or (a.trophy_type = 'player_AllTimeCareer' and a.rank <= 10)
                        , concat('- '
                            , a.new_trophy_type
                            , ' '
                            , a.new_trophy_name
                            , if(a.rank = 1, ' Record', concat(' (', a.rank, ')'))
                            , if(a.ties > 0, concat(' (tied w/', a.ties, ' others)'), '')
                        )
                        , null
                        )
                    order by a.trophy_type asc
                    , a.rank asc
                    separator ' \n'), '')
                ) trophy_details
                from temp a
                left join(
                    select player_name
                    , h_team
                    , p_team
                    , h_years
                    , p_years
                    , sum(if(b.trophy_name != 'world series' and b.update_type != 'outliers' and b.trophy_type = 'player', b.cnt, 0)) as trophy_count
                    , group_concat(concat('- '
                        , b.cnt
                        , 'x '
                        , b.new_trophy_name
                        , if(b.trophy_type = 'player_leagueleader' and b.update_type != 'outliers', ' Leader', '')
                        , ' ('
                        , b.years
                        , ')'
                        )
                    order by if(b.trophy_name = 'World Series', 1, 0) desc
                    , if(b.trophy_type = 'player', 1, 0) desc
                    , if(b.update_type = 'outliers', 1, 0) desc
                    , b.cnt desc
                    separator ' \n') AS accolades
                    from(
                        select player_name
                        , h_team
                        , p_team
                        , h_years
                        , p_years
                        , trophy_name
                        , group_concat(distinct new_trophy_type) as combined_trophy_types
                        , trophy_type
                        , new_trophy_name
                        , update_type
                        , count(*) as cnt
                        , group_concat(distinct t.year order by t.year asc separator ', ') as years
                        from temp t
                        where 1
                            and t.trophy_type in ('player', 'player_leagueleader')
                            and case
                                when t.trophy_type = 'player_leagueleader' then t.rank <= 1
                                when t.trophy_type = 'player' then (t.update_type = 'outliers' or t.trophy_name in ('World Series', 'All Star', 'Gold Glove', 'Silver Slugger') or (t.new_trophy_type = 'award' and t.rank = 1))
                                else 1
                            end
                        group by player_name, h_team, p_team, h_years, p_years, trophy_name
                    ) b
                    group by player_name, h_team, p_team, h_years, p_years
                ) c on (a.player_name = c.player_name
                    and ifnull(a.h_team,'') = ifnull(c.h_team,'')
                    and ifnull(a.p_team,'') = ifnull(c.p_team,'')
                    and ifnull(a.h_years,'') = ifnull(c.h_years,'')
                    and ifnull(a.p_years,'') = ifnull(c.p_years,'')
                )
                group by player_name, h_team, p_team, h_years, p_years
            ) t on (h.player_name = t.player_name and h.year_span = t.%s_years and h.team = t.%s_team)
            set h.trophy_count = t.trophy_count
            , h.black_ink = t.black_ink
            , h.gray_ink = t.gray_ink
            , h.trophy_details = t.trophy_details
            where 1
                and h.group_type  = 'full_career'
            ;

            drop table if exists temp;
        """ % (hp, hp[0], hp[0])

        for q in career_queries.split(";"):
            if q.strip() != "":
                # raw_input(q)
                db.query(q)
                db.conn.commit()

def tests():
    q_dict = {"irregularities":"""select year
        , trophy_name
        , league
        , trophy_type
        , position
        , update_type
        , count(distinct update_type) as updates
        , count(distinct if(score=0,0,1)) as score_types
        , count(*) as vals
        , count(distinct rank_id) AS vals2
        , count(distinct score) as scores
        , sum(if(ties=0,0,1))-count(distinct if(ties=0,null,score)) as ties
        from trophies t1
        where 1
            and update_type not in ('leaders', 'outliers')
        group by year, trophy_name, league, trophy_type, position
        having 0
            or updates > 1
            or score_types > 1
            or vals != vals2
            or vals != (scores+ties)
            or vals2 != (scores+ties)
        ;"""
        , "player names":"""select t.*
        , group_concat(distinct t1.team_name) AS h_team
        , group_concat(distinct left(t1.division,2)) AS h_league
        , group_concat(distinct t2.team_name) AS p_team
        , group_concat(distinct left(t2.division,2)) AS p_league
        from trophies t
        left join historical_stats_hitters h on (t.year = h.year_span and t.player_name = h.player_name and h.group_type = 'season_by_team')
        left join teams t1 on (t.year = t1.year and h.team = t1.team_name and IF(t.league = '', 1, t.league = left(t1.division,2)))
        left join historical_stats_pitchers p on (t.year = p.year_span and t.player_name = p.player_name and p.group_type = 'season_by_team')
        left join teams t2 on (t.year = t2.year and p.team = t2.team_name and IF(t.league = '', 1, t.league = left(t2.division,2)))
        where 1
        and t.player_name is not null
        and t.trophy_type = 'player'
        and t.year >= 2006
        group by t.year, t.trophy_name, t.league, t.trophy_type, t.rank, t.player_name
        having 0
        or (h_team is null and p_team is null)
        or (h_team is not null and p_team is not null and player_name not in ('shohei ohtani', 'henry rodriguez'))
        ;"""
        , "group irregularities":"""select trophy_name
        , trophy_type
        , count(distinct if(update_type in ('manual', 'backfilled'), 'user', update_type)) as update_cnt
        , count(distinct league) as lg_cnt
        , count(distinct year) as yr_cnt
        from trophies
        group by trophy_name, trophy_type
        having 0
        or update_cnt >= 2
        or if(trophy_name = 'world series' and lg_cnt >= 2, 1, 0)
        or if(trophy_name != 'world series' and lg_cnt >= 3, 1, 0)
        ;"""
        , "subset of group irregularities":"""select year
        , trophy_name
        , league
        , trophy_type
        , count(distinct if(update_type in ('manual', 'backfilled'), 'user', update_type)) as update_cnt
        , count(distinct if(team_name is null, 1, 0)) as team_cnt
        , count(distinct if(player_name is null, 1, 0)) as player_cnt
        from trophies
        group by year, trophy_name, league, trophy_type
        having 0
        or update_cnt >= 2
        or team_cnt >= 2
        or player_cnt >= 2
        ;"""
    }

    print '\ttests'
    for desc, query in q_dict.items():
        print '\t\ttesting', desc
        for q in query.split(";"):
            if q.strip() != "":
                q_res = db.query(q)
                if q_res != ():
                    print '\t\t\t~~~~~~~~~ERRROR~~~~~~~~~'
                    print q


if __name__ == "__main__":
    start_time = time()

    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2021)
    parser.add_argument('--backfill',type=str,default="False")
    args = parser.parse_args()

    process(args.year, args.backfill)

    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "NSBL_awards.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)