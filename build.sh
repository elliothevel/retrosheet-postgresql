echo 'creating schema'
docker-compose exec etl psql -f db/tables.sql

echo 'loading event data'
docker-compose exec etl python load.py -s "$1" -e "$2"

echo 'creating indices'
docker-compose exec etl psql -f db/indices.sql
