/* Run expectancy for each of the 24 base/out states. */
WITH
complete_innings AS (
    SELECT game_id, inn_ct
    FROM retrosheet.events
    WHERE SUBSTR(game_id, 4, 4)::INT BETWEEN {{start_year}} AND {{end_year}}
    AND inn_ct < 9
    AND bat_home_id = 1
    AND outs_ct + event_outs_ct = 3
    GROUP BY 1,2
),
event_scores AS (
    SELECT
        *,
        CASE
            WHEN bat_home_id = 1 THEN home_score_ct
            ELSE away_score_ct
        END AS bat_score_ct,
        ((CASE WHEN bat_dest_id >= 4 THEN 1 ELSE 0 END)
         + (CASE WHEN run1_dest_id >= 4 THEN 1 ELSE 0 END)
         + (CASE WHEN run2_dest_id >= 4 THEN 1 ELSE 0 END)
         + (CASE WHEN run3_dest_id >= 4 THEN 1 ELSE 0 END)) AS event_score_ct
    FROM retrosheet.events
),
game_states AS (
    SELECT
        base1_run_id <> '' AS "1B",
        base2_run_id <> '' AS "2B",
        base3_run_id <> '' AS "3B",
        outs_ct,
        (LAST_VALUE(bat_score_ct + event_score_ct) OVER rest_of_frame
         - bat_score_ct) AS inc_score_ct
    FROM event_scores
    INNER JOIN complete_innings
        USING(game_id, inn_ct)
    WINDOW rest_of_frame AS (
        PARTITION BY game_id, inn_ct, bat_home_id
        ORDER BY event_id ASC
        RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
    )
)
SELECT
    "1B",
    "2B",
    "3B",
    ROUND(AVG(inc_score_ct) FILTER (WHERE outs_ct = 0), 3) AS "0 Outs",
    ROUND(AVG(inc_score_ct) FILTER (WHERE outs_ct = 1), 3) AS "1 Out",
    ROUND(AVG(inc_score_ct) FILTER (WHERE outs_ct = 2), 3) AS "2 Outs"
FROM game_states
GROUP BY 1,2,3
ORDER BY 1,2,3;
