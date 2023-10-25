# Web scraper for games in an NHL season

Usage: (with the command line)

```
    python scraper.py --nhl_leauge_link "https://hockey.sigmagfx.com/compseason/nhl/1819/games" --first_match 5 --last_match 10
```

the script outputs a file `output.csv`.

Column names are:

```
    "id", "stage", "date", "hometeam", "otherteam", "score", "scoretype", "location", "attendance", 
    "reportlink",

    "total_gametime",
    "penalty_tot1", "penalty_tot2", 

    "team_1_penalty_p1", "team_1_penalty_p2", "team_1_penalty_p3", "team_1_penalty_ot",
    "team_2_penalty_p1", "team_2_penalty_p2", "team_2_penalty_p3", "team_2_penalty_ot", 

    "team_1_goals_p1", "team_1_goals_p2", "team_1_goals_p3", "team_1_goals_ot",
    "team_1_shots_p1", "team_1_shots_p2", "team_1_shots_p3", "team_1_shots_ot",
    "team_2_goals_p1", "team_2_goals_p2", "team_2_goals_p3", "team_2_goals_ot",
    "team_2_shots_p1", "team_2_shots_p2", "team_2_shots_p3", "team_2_shots_ot",

    "team_1_pp_5v4_occ", "team_1_pp_5v4_goal", "team_1_pp_5v4_time",
    "team_1_pp_5v3_occ", "team_1_pp_5v3_goal", "team_1_pp_5v3_time",
    "team_1_pp_4v3_occ", "team_1_pp_4v3_goal", "team_1_pp_4v3_time",
    "team_2_pp_5v4_occ", "team_2_pp_5v4_goal", "team_2_pp_5v4_time",
    "team_2_pp_5v3_occ", "team_2_pp_5v3_goal", "team_2_pp_5v3_time",
    "team_2_pp_4v3_occ", "team_2_pp_4v3_goal", "team_2_pp_4v3_time",

    "team_1_es_5v5_occ", "team_1_es_5v5_goal", "team_1_es_5v5_time",
    "team_1_es_4v4_occ", "team_1_es_4v4_goal", "team_1_es_4v4_time",
    "team_1_es_3v3_occ", "team_1_es_3v3_goal", "team_1_es_3v3_time",
    "team_2_es_5v5_occ", "team_2_es_5v5_goal", "team_2_es_5v5_time",
    "team_2_es_4v4_occ", "team_2_es_4v4_goal", "team_2_es_4v4_time",
    "team_2_es_3v3_occ", "team_2_es_3v3_goal", "team_2_es_3v3_time",

    "team_1_goaltender_1_time", "team_1_goaltender_2_time", "team_1_empty_net_time",
    "team_2_goaltender_1_time", "team_2_goaltender_2_time","team_2_empty_net_time"

```