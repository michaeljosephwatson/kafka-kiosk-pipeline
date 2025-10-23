# pylint: disable=E0015

"""File to merge all the csv files together into one csv file"""

import csv
from argparse import ArgumentParser
import logging
logging.addLevelName(logging.INFO, "\033[32mINFO\033[0m")
logging.addLevelName(logging.WARNING, "\033[38;5;208mWARNING\033[0m")
logging.addLevelName(logging.ERROR, "\033[31mERROR\033[0m")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

BASE_PATH = "../data/lmnh_hist_data_"


def read_csv_file(file_path: str) -> list:
    """Reads a csv file and returns the data as a list of lines which will then be combined into a csv at the end"""

    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)

    with open('processed_files.txt', 'a', encoding='utf-8') as f:
        f.write(file_path + "\n")

    return data


def write_full_csv_file(min_number, max_number, overwrite: bool = True) -> None:
    """Combine numbered CSV files into one full file"""

    mode = "w" if overwrite else "a"
    header_written = mode != "w"
    output_path = "../data/kiosk_data_full.csv"

    try:
        with open(output_path, mode, encoding="utf-8", newline="") as out_f:
            writer = csv.writer(out_f)

            for i in range(min_number, max_number + 1):

                file_path = f"{BASE_PATH}{i}.csv"
                if file_path in get_processed_files():
                    logging.info("Skipping processed file: %s", file_path)
                    continue

                rows = read_csv_file(file_path)
                if not rows:
                    continue

                if not header_written:
                    writer.writerow(rows[0])
                    header_written = True

                for row in rows[1:]:
                    writer.writerow(row)

        logging.info("Combined CSV files into kiosk_data_full.csv")

    except FileNotFoundError as e:
        logging.error("File not found: %s", e)


def get_processed_files() -> list:
    """Returns a list of processed files from processed_files.txt"""

    with open('processed_files.txt', 'r', encoding='utf-8') as f:
        processed_files = f.read().splitlines()

    return processed_files


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Combine numbered CSV files into one full file")
    parser.add_argument("-o", "--overwrite", action="store_true",
                        help="Overwrite the existing full CSV file")

    parser.add_argument("-min", "--min-number", type=int, default=0,
                        help="Minimum number for the file name")
    parser.add_argument("-max", "--max-number", type=int, default=3,
                        help="Maximum number for the file name")

    args = parser.parse_args()

    write_full_csv_file(min_number=args.min_number,
                        max_number=args.max_number, overwrite=args.overwrite)
