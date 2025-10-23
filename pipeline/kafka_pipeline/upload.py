"""This file takes an entry from the consumer manipulates and uploads to the rds"""

from dotenv import dotenv_values
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
import pandas as pd


def get_connection(local: bool = False):
    """Gets a connection to the rds database"""

    config = dotenv_values()

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


def process_entry(data: pd.DataFrame) -> dict:
    """Processes the entry so it is consistent with the database"""

    data["transaction_date"] = pd.to_datetime(data["at"]).dt.date
    data["transaction_time"] = pd.to_datetime(data["at"]).dt.time
    data = data.drop(columns=["at"])

    data = data.rename(columns={"site": "exhibition_id", "val": "value"})

    data["value"] = data["value"].replace(-1, None)

    if 'type' not in data.columns:
        data["type"] = None

    data["type"] = data["type"].replace(
        {0.0: "assistance", 1.0: "emergency"})
    data = data.astype(object).where(pd.notnull(data), None)

    return data.to_dict(orient="records")


def upload_entry(data: dict) -> None:
    """Uploads a single entry that was consumed to the rds database"""

    conn = get_connection()

    with conn.cursor() as cursor:
        query = """
        INSERT INTO kiosk_transaction (transaction_date, transaction_time, exhibition_id, value, type)
        VALUES (%(transaction_date)s, %(transaction_time)s, %(exhibition_id)s, %(value)s, %(type)s)
        ON CONFLICT DO NOTHING;
        """
        cursor.execute(query, data[0])

    conn.commit()


def conduct_upload(data: dict) -> None:
    """Runs the process to upload the entry to the rds"""

    data_df = pd.DataFrame([data])
    processed_data = process_entry(data_df)
    upload_entry(processed_data)


if __name__ == "__main__":
    sample_data = {
        "at": "2024-06-15T14:30:00Z",
        "site": 1,
        "val": 5,
        "type": 0.0
    }
    conduct_upload(sample_data)
