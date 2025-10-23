set -e

set -a
source ../../.env
set +a

cd terraform_config
terraform apply

cd ../
PGPASSWORD="$AWS_RDS_PASSWORD" psql -h "$AWS_RDS_HOST" -p "$AWS_RDS_PORT" -U "$AWS_RDS_USER" -d "postgres" -f schema.sql

: > processed_files.txt

python3 extract.py -c

python3 combine.py -o

python3 upload.py