# pylint: disable=E0015

"""This file extracts all the data from the s3 bucket for the museum"""

from dotenv import dotenv_values
from boto3 import client
from argparse import ArgumentParser
import os
import glob
import logging
logging.addLevelName(logging.INFO, "\033[32mINFO\033[0m")
logging.addLevelName(logging.WARNING, "\033[38;5;208mWARNING\033[0m")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_aws_client(config: dict) -> client:
    """Returns the client connection to the s3 bucket on AWS."""

    return client(
        "s3",
        aws_access_key_id=config["ACCESS_KEY_ID"],
        aws_secret_access_key=config["SECRET_ACCESS_KEY"],
    )


if __name__ == "__main__":

    parser = ArgumentParser(
        description="Extract data files from S3 bucket")

    parser.add_argument(
        "-c", "--clear", action="store_true", help="Clear existing files in ./data/ before downloading")
    args = parser.parse_args()
    if args.clear:
        files = glob.glob("./data/*")
        for f in files:
            os.remove(f)
        logging.info("Cleared existing files in ./data/")

    config = dotenv_values()
    s3_client = get_aws_client(config)

    bucket = s3_client.list_objects_v2(Bucket="sigma-resources-museum")

    for f in bucket["Contents"]:

        if (not f["Key"].endswith(".json") and not f["Key"].endswith(".csv")):
            logging.info("Skipping %s", f['Key'])
            continue

        if not f["Key"].startswith("lmnh"):
            logging.info("Skipping %s", f['Key'])
            continue

        logging.info("Downloading %s", f['Key'])
        s3_client.download_file(
            "sigma-resources-museum", f["Key"], f"../data/{f['Key']}"
        )
