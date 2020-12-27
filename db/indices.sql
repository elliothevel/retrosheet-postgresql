CREATE INDEX ON retrosheet.events (game_id, inn_ct, bat_home_id);
CREATE INDEX ON retrosheet.events ((SUBSTR(game_id, 4, 4)::INT), inn_ct);
