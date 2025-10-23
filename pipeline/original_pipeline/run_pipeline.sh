set -e

set -a
source ../../.env
set +a

cd terraform_config
terraform apply

cd ..

python3 extract.py -c

python3 combine.py -o

python3 upload.py