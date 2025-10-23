"""This file uploads the data from kiosk_data_full.csv and the json files into the museum database."""

import os
import json
from psycopg2 import connect
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor
import pandas as pd
import logging
from dotenv import dotenv_values
from argparse import ArgumentParser
logging.addLevelName(logging.INFO, "\033[32mINFO\033[0m")
logging.addLevelName(logging.WARNING, "\033[38;5;208mWARNING\033[0m")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")


def get_connection(config: dict, local: bool) -> connection:
    """Establishes and returns a connection to the PostgreSQL RDS on AWS."""
    if not local:
        return connect(
            host=config["AWS_RDS_HOST"],
            port=config["AWS_RDS_PORT"],
            dbname=config["AWS_RDS_DBNAME"],
            user=config["AWS_RDS_USER"],
            password=config["AWS_RDS_PASSWORD"],
            cursor_factory=RealDictCursor
        )

    return connect(dbname=config["LOCAL_DBNAME"],
                   cursor_factory=RealDictCursor)


def get_json_files_to_upload() -> list[str]:
    """Returns a list of all the json files in the data folder and filters dynamically by name convention."""

    data_files = os.listdir("../data")
    files_to_upload = []
    with open('processed_files.txt', 'r', encoding='utf-8') as f:
        processed_files = f.read().splitlines()

    for file in data_files:
        if file not in processed_files and file.endswith(".json") and file.startswith("lmnh_exhibition"):
            files_to_upload.append(file)

    with open('processed_files.txt', 'a', encoding='utf-8') as f:
        for file in files_to_upload:
            f.write(f"{file}\n")

    logging.info("JSON files to upload: %s", files_to_upload)
    return files_to_upload


def get_csv_data() -> pd.DataFrame:
    """Reads the kiosk_data_full.csv file and returns its contents as a list of dictionaries.

    Must run combine.py file first to create the full csv file.
    """

    full_csv_path = "../data/kiosk_data_full.csv"

    if not os.path.exists(full_csv_path) or os.path.getsize(full_csv_path) == 0:
        logging.warning("kiosk_data_full.csv is empty or does not exist.")
        return pd.DataFrame()

    data_df = pd.read_csv(full_csv_path)
    return data_df


def process_json_data_to_correct_format() -> list[dict]:
    """Reads in the json files from the ../data folder and then extracts the exhibition data and places it into a dataframe."""

    final_frame = pd.DataFrame(
        columns=["name", "exhibition_id", "floor", "department", "start_date", "end_date", "description"])

    files_to_upload = get_json_files_to_upload()

    for file in files_to_upload:
        with open(f"../data/{file}", "r", encoding="utf-8") as f:
            json_data = json.load(f)
            temp_df = pd.json_normalize(json_data)

            # Renaming the columns to match the database
            temp_df = temp_df.rename(columns={
                "EXHIBITION_NAME": "name",
                "FLOOR": "floor",
                "DEPARTMENT": "department",
                "START_DATE": "start_date",
                "EXHIBITION_ID": "exhibition_id",
                "DESCRIPTION": "description"})

            temp_df['exhibition_id'] = temp_df['exhibition_id'].apply(
                lambda val: int(val[4:]))

            temp_df['start_date'] = pd.to_datetime(
                temp_df['start_date'], errors='coerce').dt.date

            final_frame = pd.concat(
                [final_frame, temp_df], ignore_index=True)

            final_frame = final_frame.sort_values(
                by="exhibition_id").reset_index(drop=True)

            final_frame = final_frame.drop(columns=["exhibition_id"])

    logging.info("JSON data frame processed successfully.")
    return final_frame.to_dict(orient="records")


def upload_json_data(conn: connection, data: list[dict]) -> None:
    """Batch uploads the exhibition data to the exhibition table in the database."""

    with conn.cursor() as cur:
        insert_query = """
            INSERT INTO exhibition (name, floor, department, start_date, description)
            VALUES (%(name)s, %(floor)s, %(department)s, %(start_date)s, %(description)s)
            ON CONFLICT DO NOTHING
        """
        cur.executemany(insert_query, data)
        conn.commit()


def process_csv_data_to_correct_format(data: pd.DataFrame) -> list[dict]:
    """Changes the csv data into the correct format for uploading to the database."""

    if len(data) == 0:
        logging.warning("No CSV data to process.")
        return []

    data["transaction_date"] = pd.to_datetime(data["at"]).dt.date
    data["transaction_time"] = pd.to_datetime(data["at"]).dt.time
    data = data.drop(columns=["at"])

    data = data.rename(columns={"site": "exhibition_id", "val": "value"})

    data["value"] = data["value"].replace(-1, None)
    data["type"] = data["type"].replace(
        {0.0: "assistance", 1.0: "emergency"})
    data = data.astype(object).where(pd.notnull(data), None)

    logging.info("CSV data processed successfully.")
    return data.to_dict(orient="records")


def upload_csv_data(conn: connection, data: list[dict]) -> None:
    """Batch uploads the kiosk data to the kiosk_transaction table in the database."""

    with conn.cursor() as cur:
        insert_query = """
            INSERT INTO kiosk_transaction (transaction_date, transaction_time, exhibition_id, value, type)
            VALUES (%(transaction_date)s, %(transaction_time)s, %(exhibition_id)s, %(value)s, %(type)s)
            ON CONFLICT DO NOTHING
        """
        cur.executemany(insert_query, data)
        conn.commit()


if __name__ == "__main__":

    parser = ArgumentParser(description="Upload data to the database")
    parser.add_argument(
        "-l", "--local", action="store_true", help="Use local database")
    args = parser.parse_args()

    config = dotenv_values()
    conn = get_connection(config, args.local)

    json_data = process_json_data_to_correct_format()
    upload_json_data(conn, json_data)

    csv_data = process_csv_data_to_correct_format(get_csv_data())
    upload_csv_data(conn, csv_data)

    logging.info(
        "Uploaded the JSON and CSV data to the database successfully.")

    conn.close()
