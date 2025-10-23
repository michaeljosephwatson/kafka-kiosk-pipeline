set -e

set -a
source ../../.env
set +a

cd ../original_pipeline/

./create_pipeline.sh

cd ../kafka_pipeline/

./deploy_pipeline

