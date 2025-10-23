set -e

: > processed_files.txt

psql postgres -f schema.sql

python3 extract.py -c

python3 combine.py -o

python3 upload.py -l