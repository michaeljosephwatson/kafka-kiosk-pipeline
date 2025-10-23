**What the project is for?**

The project was about streaming live feedback data from museum exhibitions. The idea is that customers would go see an exhibition and then as they leave visit the kiosk where they press their rating of the exhibition. Additionally, there would be options for calling for staff assistance and emergencies. This is then pushed to Kafka which is then consumed and placed into an AWS RDS, which is then streamed to a tableau dashboard. 

This repository can be cloned and adjusted to set up a similar system for getting data from a Kafka cluster and doing analysis on it. What would have to be changed is the sensitive resources inside of a .env, the schema for the database so it matches the data that you are using, and the data processing and uploading to the correct format. However, the steps taken broadly can be followed in your own project to achieve a similar pipeline. 

**How to install any necessary dependencies:**

Create a python a venv and install requirements.txt file

* python3 -m venv .venv
* source .venv/bin/activate
* pip3 install -r requirements.txt

Will need to set your .env to have the following properties to run every file:ß

* ACCESS_KEY_ID
* SECRET_ACCESS_KEY
* AWS_RDS_HOST
* AWS_RDS_PORT
* AWS_RDS_DBNAME
* AWS_RDS_USER
* AWS_RDS_PASSWORD
* LOCAL_DBNAME
* KAFKA_BOOTSTRAP_SERVERS
* KAFKA_SECURITY_PROTOCOL
* KAFKA_SASL_MECHANISM
* KAFKA_USERNAME
* KAFKA_PASSWORD
* KAFKA_GROUP
* KAFKA_AUTO_OFFSET
* KAFKA_TOPIC
* EC2_IP

Some of the properties will only be known for you after some set up: 

1. The Kafka cluster with the target subject must be set up

2. The RDS and EC2 after running terraform apply

3. Your local postgresql database


**How to run the project:**

1. Go into the pipeline folder and then go into either original_pipeline or kafka_pipeline

2. For original_pipeline run: ./create_pipeline_local.sh

3. For kafka_pipeline run: ./initialise_db_and_pipeline.sh and then after deploy_pipeline.sh for further deployment

