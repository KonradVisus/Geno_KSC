from datetime import datetime
import logging
import json
from typing import List

import pyodbc
import pandas as pd


TABLES = json.load(open("config.json", encoding="UTF-8"))["TABLE_NAMES"]


def get_db() -> pyodbc.Connection:
    """
    Retrieves a connection to the database.

    Returns:
        pyodbc.Connection: The database connection object.
    """
    server = json.load(open("config.json", encoding="UTF-8"))["SERVER"]
    database = json.load(open("config.json", encoding="UTF-8"))["DATABASE"]
    username = json.load(open("config.json", encoding="UTF-8"))["AUTHENTICATION"][
        "USERNAME"
    ]
    password = json.load(open("config.json", encoding="UTF-8"))["AUTHENTICATION"][
        "PASSWORD"
    ]
    cnxn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + server
        + ";DATABASE="
        + database
        + ";UID="
        + username
        + ";PWD="
        + password,
        timeout=60,
    )
    return cnxn


def check_database_connection() -> None:
    """
    Checks the availability of the database connection.

    This function attempts to establish a connection to the database and then closes it.
    If the connection is successful, it logs a message indicating that the database connection is available.
    If an exception occurs during the connection attempt, it logs an error message and exits the program.

    """
    try:
        cnxn = get_db()
        cnxn.close()
        logging.info("Database connection available")
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        exit(1)


def create_correspondence(t: datetime) -> None:
    """
    Creates a new table in the database for storing customer correspondence.

    Args:
        t (datetime): The timestamp used to generate the table name.

    Returns:
        None
    """
    cnxn = get_db()
    cursor = cnxn.cursor()
    table_name = TABLES["Kunden Korrespondenz"] + t.strftime("_%Y")
    try:
        cursor.execute(
            f"IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{table_name}') CREATE TABLE {table_name} (Zeitstempel date, Anzahl int)"
        )
        cnxn.commit()
        cnxn.close()
        logging.info(f"Created table {table_name}")
    except Exception as e:
        cnxn.close()
        logging.error(f"Could not create table {table_name}: {e}")


def create_mail_order(t: datetime) -> None:
    """
    Creates a table in the database for storing mail orders, if it does not already exist. The table name is generated based on the provided timestamp.

    Args:
        t (datetime): The timestamp used to generate the table name.

    Returns:
        None
    """
    cnxn = get_db()
    cursor = cnxn.cursor()
    table_name = TABLES["Mail Order"] + t.strftime("_%Y")
    try:
        cursor.execute(
            f"IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{table_name}') CREATE TABLE {table_name} (Zeitstempel datetime, Kunde nvarchar(255), Titel nvarchar(255))"
        )
        cnxn.commit()
        cnxn.close()
        logging.info(f"Created table {table_name}")
    except Exception as e:
        cnxn.close()
        logging.error(f"Could not create table {table_name}: {e}")


def create_mail_service(t: datetime) -> None:
    """
    Creates a table in the database for the mail service, if it does not already exist. The table name is generated based on the provided timestamp.

    Args:
        t (datetime): The timestamp used to create the table name.

    Returns:
        None
    """
    cnxn = get_db()
    cursor = cnxn.cursor()

    table_name = TABLES["Mail Service"] + t.strftime("_%Y")

    try:
        cursor.execute(
            f"IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{table_name}') CREATE TABLE {table_name} (Zeitstempel datetime, Kunde nvarchar(255), Titel nvarchar(255))"
        )
        cnxn.commit()
        logging.info(f"Created table {table_name}")
        cnxn.close()
    except Exception as e:
        logging.error(f"Could not create table {table_name}: {e}")
        cnxn.close()


def create_vak(t: datetime) -> None:
    """
    Creates a table in the database for storing VAK data, if it does not already exist. The table name is generated based on the provided timestamp.

    Args:
        t (datetime): The datetime for which the table should be created.

    Returns:
        None
    """
    cnxn = get_db()
    cursor = cnxn.cursor()
    table_name = TABLES["VAK"] + t.strftime("_%Y")
    try:
        cursor.execute(
            f"IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{table_name}') CREATE TABLE {table_name}(Zeitstempel datetime, Anzahl int, Durchschnitt time(0))"
        )
        cnxn.commit()
        cnxn.close()
        logging.info(f"Created table {table_name}")
    except Exception as e:
        logging.error(f"Could not create table {table_name}: {e}")
        cnxn.close()


def create_kpis(t: datetime) -> None:
    """
    Create a table in the database for storing KPIs, if it does not already exist. The table name is generated based on the provided timestamp.

    Args:
        t (datetime): The timestamp used to generate the table name.

    Returns:
        None
    """
    cnxn = get_db()
    cursor = cnxn.cursor()
    table_name = TABLES["KPIS"] + t.strftime("_%Y")

    try:
        cursor.execute(
            f"CREATE TABLE {table_name} (Zeitstempel varchar(255), Gesamt_Minuten_Korrespondenz int, Personal_Kapazität_Korrespondenz float, Gesamt_Minuten_Order int, Personal_Kapazität_Order float, Gesamt_Minuten_Service int, Personal_Kapazität_Service float, Gesamt_Minuten_VAK int, Personal_Kapazität_VAK float)"
        )
        logging.info(f"Created table {table_name}")
        cnxn.commit()
        cnxn.close()
    except Exception as e:
        logging.error(f"Could not create table {table_name}: {e}")
        cnxn.close()


from typing import List
from datetime import datetime


def determine_missing_kpis(t: datetime) -> List[int]:
    """
    Determines the missing months for a given datetime.

    Args:
        t (datetime): The datetime for which missing months need to be determined.

    Returns:
        List[int]: A list of missing months (as integers) for the given datetime.
    """
    cnxn = get_db()
    cursor = cnxn.cursor()
    table_name = TABLES["KPIS"] + t.strftime("_%Y")
    current_month = t.month

    # get KPI rows check which month is not in the table
    cursor.execute(f"SELECT Zeitstempel FROM {table_name}")
    rows = cursor.fetchall()
    months = [int(row[0].split("-")[1]) for row in rows]
    missing_months = [m for m in range(1, current_month + 1) if m not in months]
    cnxn.close()
    return missing_months


def upsert_mail_order(t: datetime, df: pd.DataFrame, months: List[int]):

    table_name = TABLES["Mail Order"] + t.strftime("_%Y")

    df = df[df["Zeitstempel"].dt.month.isin(months)]

    cnxn = get_db()
    cursor = cnxn.cursor()

    try:
        for _, row in df.iterrows():
            cursor.execute(
                f"INSERT INTO {table_name} (Zeitstempel, Kunde, Titel) VALUES (?, ?, ?)",
                row["Zeitstempel"],
                row["Kunde"],
                row["Titel"],
            )
        cnxn.commit()
        cnxn.close()
        logging.info(f"Sucessfully upsert data into{table_name} for months {months}")
    except Exception as e:
        logging.error(f"Could not upsert data into {table_name}: {e}")
        cnxn.close()
        exit(1)


def upsert_mail_service(t: datetime, df: pd.DataFrame, months: List[int]):

    table_name = TABLES["Mail Service"] + t.strftime("_%Y")

    df = df[df["Zeitstempel"].dt.month.isin(months)]

    cnxn = get_db()
    cursor = cnxn.cursor()

    try:
        for _, row in df.iterrows():
            cursor.execute(
                f"INSERT INTO {table_name} (Zeitstempel, Kunde, Titel) VALUES (?, ?, ?)",
                row["Zeitstempel"],
                row["Kunde"],
                row["Titel"],
            )
            cnxn.commit()
            cnxn.close()
        logging.info(f"Sucessfully upsert data into {table_name} for months {months}")

    except Exception as e:
        logging.error(f"Could not upsert data into {table_name}: {e}")
        cnxn.close()
        exit(1)


def upsert_correspondence(t: datetime, df: pd.DataFrame, months: List[int]):

    table_name = TABLES["Kunden Korrespondenz"] + t.strftime("_%Y")

    df = df[df["Zeitstempel"].dt.month.isin(months)]

    cnxn = get_db()
    cursor = cnxn.cursor()
    try:
        cursor.execute(
            f"INSERT INTO {table_name} (Zeitstempel, Anzahl) VALUES (?, ?)",
            df["Zeitstempel"][0],
            int(df["Anzahl"][0]),
        )
        cnxn.commit()
        cnxn.close()
        logging.info(f"Upsert data into {table_name}")
    except Exception as e:
        logging.error(f"Could not upsert data into {table_name}: {e}")
        cnxn.close()
        exit(1)


def upsert_vak(t: datetime, df: pd.DataFrame, months: List[int]):

    table_name = TABLES["VAK"] + t.strftime("_%Y")

    df = df[df["Zeitstempel"].dt.month.isin(months)]

    cnxn = get_db()
    cursor = cnxn.cursor()

    try:
        cursor = cnxn.cursor()
        for _, row in df.iterrows():
            cursor.execute(
                f"INSERT INTO {table_name} (Zeitstempel, Anzahl, Durchschnitt) VALUES (?,?,?)",
                (row["Zeitstempel"], row["Anzahl"], row["Durchschnitt"]),
            )
        cnxn.commit()
        logging.info(f"Upsert data into {table_name}")
    except Exception as e:
        logging.error(f"Could not upsert data into {table_name}: {e}")
        cnxn.close()
        exit(1)
