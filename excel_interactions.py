from datetime import datetime
from typing import List
import logging

import pandas as pd

from utils import find_matching_file, remove_timeinterval


def check_file_existence(sources, input_dirs, file_names):
    """
    Check the existence of files based on the specified file patterns.

    This function iterates through the `sources` list and checks if any files exist
    based on the file patterns generated from the `input_dirs` and `file_names` dictionaries.
    If no files are found for a particular source, an error message is logged and the program exits.

    Note: This function assumes that the `sources`, `input_dirs`, and `file_names` variables are defined.

    Returns:
        None
    """
    for source in sources:
        file_names = find_matching_file(input_dirs[source], file_names[source])
        logging.info(f"File found for {source}: {file_names}")
    logging.info("All files found.")


def read_mail_order(
    input_path: str, file_name: str, selected_months: List[int]
) -> pd.DataFrame:

    file_name = find_matching_file(input_path, file_name)

    df = pd.read_excel(
        file_name,
        usecols=[2, 5, 7],
        names=["Kunde", "Titel", "Zeitstempel"],
        na_filter=True,
    )
    df["Kunde"] = df["Kunde"].apply(lambda x: x[:255] if isinstance(x, str) else x)
    df["Titel"] = df["Titel"].apply(lambda x: x[:255] if isinstance(x, str) else x)

    # filter all rows where 'Zeitstempel' is in the same month and as in months
    df = df[df["Zeitstempel"].dt.month.isin(selected_months)]

    # replace all NaN values with "NA"
    df = df.fillna("NA")

    if df.empty:
        logging.error("No data available for Mail Order")
        exit(1)
    return df


def read_mail_service(
    input_path: str, file_name: str, selected_months: List[int]
) -> pd.DataFrame:

    file_name = find_matching_file(input_path, file_name)

    df = pd.read_excel(
        file_name,
        usecols=[2, 5, 7],
        names=["Kunde", "Titel", "Zeitstempel"],
        na_filter=True,
    )
    df = df.dropna()
    df["Kunde"] = df["Kunde"].apply(lambda x: x[:255] if isinstance(x, str) else x)
    df["Titel"] = df["Titel"].apply(lambda x: x[:255] if isinstance(x, str) else x)
    df = df[df["Zeitstempel"].dt.month.isin(selected_months)]

    # replace all NaN values with "NA"
    df = df.fillna("NA")

    if df.empty:
        logging.error("No data available for Mail Service")
        exit(1)
    return df


def read_correspondence(
    input_path: str, file_name: str, selected_months: List[int]
) -> pd.DataFrame:
    file_name = find_matching_file(input_path, file_name)
    df = pd.read_excel(
        file_name,
        usecols=[0, 1],
        names=["Anzahl", "Zeitstempel"],
        na_filter=True,
    )
    # replace all NaN values with "NA"
    df = df.fillna("NA")

    # Convert 'Zeitstempel' to datetime
    df["Zeitstempel"] = pd.to_datetime(df["Zeitstempel"])

    # filter all rows where 'Zeitstempel' is in the same month and as in months
    df = df[df["Zeitstempel"].dt.month.isin(selected_months)]

    if df.empty:
        logging.error("No data available for Correspondence")
        exit(1)

    return df


def read_vak(
    input_path: str, file_name: str, selected_months: List[int]
) -> pd.DataFrame:
    file_name = find_matching_file(input_path, file_name)
    df = pd.read_excel(
        file_name,
        usecols=[0, 1, 2],
        names=["Zeitstempel", "Anzahl", "Durchschnitt"],
        na_filter=True,
    )
    df = df.fillna("NA")

    df["Zeitstempel"] = df["Zeitstempel"].apply(remove_timeinterval)

    df["Zeitstempel"] = pd.to_datetime(df["Zeitstempel"])

    # filter all rows where 'Zeitstempel' is in the same month and as in months
    df = df[df["Zeitstempel"].dt.month.isin(selected_months)]

    if df.empty:
        logging.error("No data available for VAK")
        exit(1)

    return df


def available_data(
    df_mail_order: pd.DataFrame,
    df_mail_service: pd.DataFrame,
    df_correspondence: pd.DataFrame,
    df_vak: pd.DataFrame,
) -> List[int]:
    """
    Returns a list of months for which data is available in all four input DataFrames.

    Args:
        df_mail_order (pd.DataFrame): DataFrame containing mail order data.
        df_mail_service (pd.DataFrame): DataFrame containing mail service data.
        df_correspondence (pd.DataFrame): DataFrame containing correspondence data.
        df_vak (pd.DataFrame): DataFrame containing vak data.

    Returns:
        List[int]: List of months for which data is available in all four DataFrames.
    """

    mail_order_months = df_mail_order["Zeitstempel"].dt.month.unique()
    mail_service_months = df_mail_service["Zeitstempel"].dt.month.unique()
    correspondence_months = df_correspondence["Zeitstempel"].dt.month.unique()
    vak_months = df_vak["Zeitstempel"].dt.month.unique()

    available_months = [
        month
        for month in mail_order_months
        if month in mail_service_months
        and month in correspondence_months
        and month in vak_months
    ]

    return available_months
