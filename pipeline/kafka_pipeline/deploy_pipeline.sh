set -e

set -a
source ../../.env
set +a

cd terraform_config
terraform apply

cd ../../original_pipeline/

python3 extract.py -c 

cd ../kafka_pipeline

ssh -i .pemkey ec2-user@$EC2_IP "[ -d pipeline ] || mkdir pipeline"

scp -i .pemkey consumer.py ec2-user@$EC2_IP:./pipeline

scp -i .pemkey upload.py ec2-user@$EC2_IP:./pipeline

scp -i .pemkey requirements.txt ec2-user@$EC2_IP:./pipeline

scp -i .pemkey ../../.env ec2-user@$EC2_IP:.

scp -i .pemkey -r ../data ec2-user@$EC2_IP:.

ssh -i .pemkey ec2-user@$EC2_IP "
  cd pipeline

  sudo apt-get update
  sudo apt-get install -y python3 python3-pip python3-venv

  python3 -m venv .venv
  source .venv/bin/activate

  pip install --upgrade pip
  pip install -r requirements.txt

  pkill -f 'consumer.py'
  nohup python3 consumer.py > consumer.log 2>&1 &
"
