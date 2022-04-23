from py_db import db
from time import time
import argparse

# Makes a string that preps the weekly post

db = db('NSBL')

def process(year):

    qry = """select grouping
        , if(grouping in ('top','bottom'), team_name, group_concat(spreadsheet_abb order by abs(weekly_impv) desc separator ', ')) as team
        , if(grouping in ('top','bottom'), upper(team_abb), null) as team_abb
        , if(grouping in ('top','bottom'), concat(week_w, '-', week_l), null) as wl
        , if(grouping in ('top','bottom'), concat(if(left(win_World_Series_change,1)='-','','+'), win_World_Series_change), null) as ws
        , if(grouping in ('top','bottom'), games_won_change, null) as gw
        from(
            select wc.*
            , tb.*
            , t.spreadsheet_abb 
            , case
                when rank = 1 then 'top'
                when rank = 30 then 'bottom'
                when weekly_impv >= 0.75*top then 'top_also'
                when weekly_impv <= .75*bottom then 'bottom_also'
            end as
            grouping
            from __weekly_changes wc
            join teams t on (wc.year = t.year and wc.team_name = t.team_name)
            join(
                select max(weekly_impv) as top
                , min(weekly_impv) as bottom
                from __weekly_changes
            ) tb
        ) b
        where 1
            and grouping is not null
        group by grouping 
    ;"""

    res = db.query(qry)

    res_dict = {"top":[""],"bottom":[""],"top_also":[""],"bottom_also":[""]}
    for row in res:
        grouping, team, team_abb, wl, ws, gw = row 
        res_dict[grouping] = [team, team_abb, wl, ws, gw]

    db.query("set session group_concat_max_len = 1000000;")
    db.conn.commit()

    q2 = """select group_concat(awards order by rn asc separator '\n') as res
        from(
            select @rownum:=1 as rn, 'AL MVP:' as awards
            union all
            select @rownum:=@rownum+1, a.*
            from(
                select group_concat(concat(ranking
                    , '. '
                    , player_name
                    , ' (', upper(position), ')'
                    , ' - '
                    , teams
                    )
                order by ranking separator '\n') as ranks
                from temp_mvp
                where year = %s
                    and league = 'al'
                    and ranking <= 10
                order by cast(ranking as signed)
            ) a
            
            union all
            select @rownum:=@rownum+1 as rn, '\nNL MVP:' as awards
            union all
            select @rownum:=@rownum+1, a.*
            from(
                select group_concat(concat(ranking
                    , '. '
                    , player_name
                    , ' (', upper(position), ')'
                    , ' - '
                    , teams
                    )
                order by ranking separator '\n') as ranks
                from temp_mvp
                where year = %s
                    and league = 'nl'
                    and ranking <= 10
                order by cast(ranking as signed)
            ) a
            
            union all
            select @rownum:=@rownum+1 as rn, '\nAL Cy Young:' as awards
            union all
            select @rownum:=@rownum+1, a.*
            from(
                select group_concat(concat(ranking
                    , '. '
                    , player_name
                    , ' (', upper(position), ')'
                    , ' - '
                    , teams
                    )
                order by ranking separator '\n') as ranks
                from temp_cy_young
                where year = %s
                    and league = 'al'
                    and ranking <= 5
                order by cast(ranking as signed)
            ) a
            
            union all
            select @rownum:=@rownum+1 as rn, '\nNL Cy Young:' as awards
            union all
            select @rownum:=@rownum+1, a.*
            from(
                select group_concat(concat(ranking
                    , '. '
                    , player_name
                    , ' (', upper(position), ')'
                    , ' - '
                    , teams
                    )
                order by ranking separator '\n') as ranks
                from temp_cy_young
                where year = %s
                    and league = 'nl'
                    and ranking <= 5
                order by cast(ranking as signed)
            ) a
            
            union all
            select @rownum:=@rownum+1 as rn, '\nAL Rookie of the Year:' as awards
            union all
            select @rownum:=@rownum+1, a.*
            from(
                select group_concat(concat(ranking
                    , '. '
                    , player_name
                    , ' (', upper(position), ')'
                    , ' - '
                    , teams
                    )
                order by ranking separator '\n') as ranks
                from temp_rookie_of_the_year
                where year = %s
                    and league = 'al'
                    and ranking <= 5
                order by cast(ranking as signed)
            ) a
            
            union all
            select @rownum:=@rownum+1 as rn, '\nNL Rookie of the Year:' as awards
            union all
            select @rownum:=@rownum+1, a.*
            from(
                select group_concat(concat(ranking
                    , '. '
                    , player_name
                    , ' (', upper(position), ')'
                    , ' - '
                    , teams
                    )
                order by ranking separator '\n') as ranks
                from temp_rookie_of_the_year
                where year = %s
                    and league = 'nl'
                    and ranking <= 5
                order by cast(ranking as signed)
            ) a
            
            union all
            select @rownum:=@rownum+1 as rn, '\nAL Hank Aaron Award:' as awards
            union all
            select @rownum:=@rownum+1, a.*
            from(
                select group_concat(concat(ranking
                    , '. '
                    , player_name
                    , ' (', upper(position), ')'
                    , ' - '
                    , teams
                    )
                order by ranking separator '\n') as ranks
                from temp_hank_aaron
                where year = %s
                    and league = 'al'
                    and ranking <= 3
                order by cast(ranking as signed)
            ) a
            
            union all
            select @rownum:=@rownum+1 as rn, '\nNL Hank Aaron Award:' as awards
            union all
            select @rownum:=@rownum+1, a.*
            from(
                select group_concat(concat(ranking
                    , '. '
                    , player_name
                    , ' (', upper(position), ')'
                    , ' - '
                    , teams
                    )
                order by ranking separator '\n') as ranks
                from temp_hank_aaron
                where year = %s
                    and league = 'nl'
                    and ranking <= 3
                order by cast(ranking as signed)
            ) a
            
            union all
            select @rownum:=@rownum+1 as rn, '\nAL Reliever of the Year:' as awards
            union all
            select @rownum:=@rownum+1, a.*
            from(
                select group_concat(concat(ranking
                    , '. '
                    , player_name
                    , ' (', upper(position), ')'
                    , ' - '
                    , teams
                    )
                order by ranking separator '\n') as ranks
                from temp_reliever_of_the_year
                where year = %s
                    and league = 'al'
                    and ranking <= 3
                order by cast(ranking as signed)
            ) a
            
            union all
            select @rownum:=@rownum+1 as rn, '\nNL Reliever of the Year:' as awards
            union all
            select @rownum:=@rownum+1, a.*
            from(
                select group_concat(concat(ranking
                    , '. '
                    , player_name
                    , ' (', upper(position), ')'
                    , ' - '
                    , teams
                    )
                order by ranking separator '\n') as ranks
                from temp_reliever_of_the_year
                where year = %s
                    and league = 'nl'
                    and ranking <= 3
                order by cast(ranking as signed)
            ) a
        ) b
    ;""" % (year, year, year, year, year, year, year, year, year, year)

    ldrs = db.query(q2)[0][0]

    post = """\n\n\nThe good: 

The bad: 

Coming up: 

[hr]

[b]AWARD LADDERS[/b]
%s

[hr]

[b]MILESTONE WATCH[/b]
[a href="http://connor-r.github.io/Tables/NSBL_milestones.html"]Milestone Watch[/a]

[hr]

Weekly Leaderboards are updated:
[ul type="disc"]
[li][a href="http://connor-r.github.io/Tables/leaderboard_Standings.html"]Advanced Standings[/a][/li]
[li][a href="http://connor-r.github.io/Tables/leaderboard_Changes.html"]Weekly Changes[/a][/li]
[li][a href="http://connor-r.github.io/Tables/historical_StatsPitchers.html"]Pitchers[/a][a][/a][/li]
[li][a href="http://connor-r.github.io/Tables/historical_StatsHitters.html"]Batters[/a][/li]
[/ul]

[hr]

[a href="http://connor-r.github.io/Posts/sim_league_weekly_charts.html"]Week-By-Week Charts[/a]

Best week: %s, %s, %s World Series Odds (%s wins added to mean win projection). Also Considered: %s
[img style="max-width:40%%;" src="http://connor-r.github.io/i/NSBL_WeeklyProjections/2021_%s-WeeklyProjections.png" alt=" "]

Worst week: %s, %s, %s World Series Odds (%s wins subtracted from mean win projection). Also Considered: %s
[img style="max-width:40%%;" src="http://connor-r.github.io/i/NSBL_WeeklyProjections/2021_%s-WeeklyProjections.png" alt=" "]


[img alt=" " src="http://connor-r.github.io/i/NSBL_WeeklyProjections/2021_NSBL_Wins-WeeklyProjections.png" style="max-width:50%%;"]
[img style="max-width:50%%;" alt=" " src="http://connor-r.github.io/i/NSBL_WeeklyProjections/2021_NSBL_PlayoffOdds-WeeklyProjections.png"]
[img src="http://connor-r.github.io/i/NSBL_WeeklyProjections/2021_NSBL_WorldSeriesOdds-WeeklyProjections.png" alt=" " style="max-width:50%%;"]
[div align="justify"][/div]""" % (ldrs
        , res_dict.get('top')[0]
        , res_dict.get('top')[2]
        , res_dict.get('top')[3]
        , res_dict.get('top')[4]
        , res_dict.get('top_also')[0] or ""
        , res_dict.get('top')[1]
        , res_dict.get('bottom')[0]
        , res_dict.get('bottom')[2]
        , res_dict.get('bottom')[3]
        , res_dict.get('bottom')[4]
        , res_dict.get('bottom_also')[0] or ""
        , res_dict.get('bottom')[1]
    )

    print post


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2021)
    args = parser.parse_args()

    process(args.year)
