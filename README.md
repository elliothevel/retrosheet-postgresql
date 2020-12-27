## retrosheet-postgresql

A dockerized environment for working with
[Retrosheet](https://www.retrosheet.org) data
in a PostgreSQL database.

### Usage

Start the docker services
```
$ docker-compose up -d
```

Build the database and load Retrosheet data
```
$ ./build.sh 1990 1999
```
(substitute different years as desired).

Use an interactive interpreter
```
$ ./interpreter

postgres=# select game_id, pit_id, count(*)
postgres-# from retrosheet.events
postgres-# where event_cd = 3
postgres-# group by 1,2
postgres-# order by 3 desc,2
postgres-# limit 5;
   game_id    |  pit_id  | count
--------------+----------+-------
 DET199609180 | clemr001 |    20
 CHN199805060 | woodk002 |    20
 PHI199110060 | coned001 |    19
 SEA199706240 | johnr005 |    19
 SEA199708080 | johnr005 |    19
(5 rows)

```

### Acknowledgments
```
The information used here was obtained free of
charge from and is copyrighted by Retrosheet. Interested
parties may contact Retrosheet at "www.retrosheet.org".
```
