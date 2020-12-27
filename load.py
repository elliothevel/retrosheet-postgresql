"""Load Retrosheet event data into a PostgreSQL database.

This script requires database connection parameters to be set
in environment variables such as `PGHOST` and `PGUSER`. For
more information, see
https://www.postgresql.org/docs/current/libpq-envars.html.

It also requires BEVENT.exe and BGAME.exe executable files
to be discoverable by wine. This can be configured by setting
the `WINEPATH` environment variable, e.g.,
`export WINEPATH=$(winepath -w path/to/exe)`.
To obtain the executables themselves, see
https://www.retrosheet.org/tools.htm.
"""
import argparse
import logging
import subprocess
import sys
import tempfile
import zipfile

import psycopg2
import requests


EVENTS_URL = 'https://retrosheet.org/events/{:d}eve.zip'


def main():
    parser = argparse.ArgumentParser(description='Load Retrosheet events')
    parser.add_argument('-s', '--start-year', type=int, required=True)
    parser.add_argument('-e', '--end-year', type=int, required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    years = range(args.start_year, args.end_year + 1)

    conn = psycopg2.connect('')
    with conn:
        for year in years:
            download_and_copy(conn, year)

    conn.close()


def download_and_copy(conn, year):
    """Process one year of event data.

    Downloads, extracts, parses, and copies event data
    for a single year.
    """
    with tempfile.TemporaryDirectory() as data_dir:
        download_events(year, data_dir)
        with conn.cursor() as curs:
            copy_events(curs, year, data_dir)
            copy_games(curs, year, data_dir)


def download_events(year, data_dir):
    """Download and extract event files.

    Downloads a zip archive containing a single year of events
    from retrosheet.org and extracts its contents into the given
    directory.
    """
    logging.info('downloading events for %d', year)
    url = EVENTS_URL.format(year)
    with tempfile.TemporaryFile() as fp:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=1024):
                fp.write(chunk)
        fp.seek(0)
        with zipfile.ZipFile(fp) as z:
            z.extractall(data_dir)


def copy_events(curs, year, data_dir):
    """Copy event data into the database.

    Parses raw event data into CSV format using Retrosheet's
    BEVENT tool. Copies the output into the events table.
    """
    logging.info('copying events for %d', year)
    with tempfile.TemporaryFile() as csv:
        subprocess.run(
            ('wine', 'BEVENT.exe',
             '-y', str(year),
             '-f', '0-96',
             '*.EV*'),
            cwd=data_dir, stdout=csv
        )
        csv.seek(0)
        curs.copy_expert('COPY retrosheet.events FROM STDIN CSV', csv)


def copy_games(curs, year, data_dir):
    """Copy game data into the database.

    Parses raw event data into CSV format using Retrosheet's
    BGAME tool. Copies the output into the games table.
    """
    logging.info('copying games for %d', year)
    with tempfile.TemporaryFile() as csv:
        subprocess.run(
            ('wine', 'BGAME.exe',
             '-y', str(year),
             '-f', '0-83',
             '*.EV*'),
            cwd=data_dir, stdout=csv
        )
        csv.seek(0)
        curs.copy_expert('COPY retrosheet.games FROM STDIN CSV', csv)


if __name__ == '__main__':
    main()
