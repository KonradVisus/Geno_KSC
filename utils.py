import math
import os
import json
import glob
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pyodbc


import logging


def find_matching_file(input_path: str, file_name: str) -> str:
    """
    Find a file in the given input path that matches the specified file name pattern.

    Args:
        input_path (str): The path to search for the file.
        file_name (str): The name pattern of the file to find.

    Returns:
        str: The path of the matched file.

    """
    search_pattern = os.path.join(input_path, "*" + file_name + "*.xlsx")
    matched_files = glob.glob(search_pattern)
    if not matched_files:
        logging.error(f"No file matching pattern '{search_pattern}' found.")
        exit(1)
    if len(matched_files) > 1:
        logging.error(f"Multiple files found for pattern '{search_pattern}'.")
        exit(1)
    return matched_files[0]


def config_logging():
    """
    Configures the logging settings.

    This function sets up the logging module with the specified settings,
    including the log file name, log level, and log message format.

    Args:
        None

    Returns:
        None
    """
    logging.basicConfig(
        filename="log.txt",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.basicConfig(
        filename="log.txt",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def remove_timeinterval(timeinterval: str) -> datetime:
    """
    remove the end of the timeinterval string
    2023-01-01 02:30-02:45 -> 2023-01-01 02:30
    """
    res = ""
    for t in timeinterval.split("-")[:-1]:
        res += t + "-"

    return res[:-1]
