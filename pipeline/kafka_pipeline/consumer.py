from confluent_kafka import Consumer
from dotenv import dotenv_values
import logging
import json
import os
import re
from datetime import datetime
from upload import conduct_upload
logging.addLevelName(logging.INFO, "\033[32mINFO\033[0m")
logging.addLevelName(logging.WARNING, "\033[38;5;208mWARNING\033[0m")
logging.addLevelName(logging.ERROR, "\033[31mERROR\033[0m")
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

DATA_DIR_PATH = '../data'


def get_message(consumer: Consumer) -> None:
    """Receives messages from the lmnh topic and will process the result"""

    while True:
        msg = consumer.poll(1)
        if msg is None:
            continue

        if msg.error():
            logging.error("Error: %s", msg.error())
            continue

        validated_data = validate_data(msg.value().decode('utf-8'))

        if validated_data is None:
            logging.error(
                "Invalid data received, skipping entry %s", msg.value().decode('utf-8'))
            continue

        logging.info("Received message: %s", validated_data)

        conduct_upload(validated_data)

        logging.info("Uploaded message to database successfully.")


def check_current_exhibitions(exhibition: str) -> bool:
    """Checks if the data is from a current exhibition returns true if it is false otherwise"""

    data_files = os.listdir(DATA_DIR_PATH)
    exhibition_files = [file for file in data_files if re.match(
        r'lmnh_exhibition\w+\.json', file)]

    file_exhibition_ids = []
    for file in exhibition_files:
        with open(f'{DATA_DIR_PATH}/{file}', 'r', encoding='utf-8') as f:
            exhibition_data = json.load(f)
            file_exhibition_ids.append(exhibition_data['EXHIBITION_ID'])

    valid_exhibition_ids = [str(int(id[-2:])) for id in file_exhibition_ids]

    return exhibition in valid_exhibition_ids


def is_valid_timestamp(timestamp: datetime) -> bool:
    """ Validates the timestamp in the context of the museum's operating hours.
    Return true if within allowed extended window (08:45–18:15)"""

    early_threshold = timestamp.replace(
        hour=8, minute=45, second=0, microsecond=0)
    late_threshold = timestamp.replace(
        hour=18, minute=15, second=0, microsecond=0)

    return early_threshold <= timestamp <= late_threshold


def validate_data(message: str) -> str:
    """Cleans the data received from Kafka"""

    data = json.loads(message)

    exhibition = data.get('site')
    timestamp_str = data.get('at')
    entry_type = data.get('type')
    value = data.get('val')

    if exhibition is None or timestamp_str is None or value is None:
        print()
        logging.error('Missing required keys in data')
        return None

    # Data Keys
    established_keys = ["site", "at", "type", "val"]
    for data_key in data.keys():
        if data_key.strip() not in established_keys:
            print()
            logging.error('Unexpected key in data: %s', data_key)
            return None

    # Exhibitions
    if not check_current_exhibitions(exhibition):
        print()
        logging.error('Invalid exhibition ID: %s', exhibition)
        return None

    # Timestamps
    timestamp = datetime.fromisoformat(timestamp_str)

    if not is_valid_timestamp(timestamp):
        print()
        logging.error('Invalid timestamp: %s', timestamp)
        return None

    # Types
    if str(entry_type) not in ['0', '1'] and entry_type is not None:
        print()
        logging.error('Invalid entry type: %s', entry_type)
        return None

    # Values
    if value not in [4, 3, 2, 1, 0, -1]:
        print()
        logging.error('Invalid value: %s', value)
        return None

    # Edge case: if value is -1 type must not be None
    if value == -1 and entry_type is None:
        print()
        logging.error('Type must not be None when value is -1')
        return None

    return data


if __name__ == "__main__":

    config = dotenv_values()

    consumer = Consumer({
        'bootstrap.servers': config['KAFKA_BOOTSTRAP_SERVERS'],
        'security.protocol': config['KAFKA_SECURITY_PROTOCOL'],
        'sasl.mechanism': config['KAFKA_SASL_MECHANISM'],
        'sasl.username': config['KAFKA_USERNAME'],
        'sasl.password': config['KAFKA_PASSWORD'],
        'group.id': config['KAFKA_GROUP'],
        'auto.offset.reset': config['KAFKA_AUTO_OFFSET']
    })

    consumer.subscribe([config['KAFKA_TOPIC']])
    logging.info("Created Consumer and subscribed to topic: %s, with group id: %s",
                 config['KAFKA_TOPIC'], config['KAFKA_GROUP'])

    get_message(consumer)
    consumer.close()
