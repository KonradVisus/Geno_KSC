from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta
import holidays
import numpy as np
import logging
import json


BZ = json.load(open("config.json", encoding="UTF-8"))["PARAMETER"]["BZ"]


def round_up(n, decimals=0):
    """
    Round up a number to a specified number of decimal places.

    Args:
        n (float): The number to be rounded up.
        decimals (int, optional): The number of decimal places to round up to. Defaults to 0.

    Returns:
        float: The rounded up number.
    """
    return np.ceil(n * 10**decimals) / (10**decimals)


def get_workdays(t: datetime, months: List[int]) -> int:
    """
    Calculate the number of working days between the last month and the current month,
    excluding German holidays in the state of Hessen.

    Returns:
        int: The number of working days.
    """
    current_year = int(t.year)

    # Get German holidays
    de_holidays = holidays.Germany(years=[current_year, current_year + 1], prov="HE")

    # Convert holidays to a format suitable for numpy
    np_holidays = [str(date) for date in de_holidays.keys()]

    # Calculate working days excluding holidays
    working_days = {}
    for month in months:
        start_date = datetime(current_year, month, 1)
        end_date = start_date + relativedelta(months=1)
        # Ensure start_date and end_date are in the correct format
        start_date_np = np.datetime64(start_date, "D")
        end_date_np = np.datetime64(end_date, "D")
        working_days[month] = np.busday_count(
            start_date_np, end_date_np, holidays=np_holidays
        )
    return working_days


def personnel_cap(total_minutes: float, t: datetime) -> float:
    """
    Calculates the personnel capacity based on the total minutes and the given date.

    Args:
        total_minutes (float): The total number of minutes.
        t (datetime): The date for which the personnel capacity is calculated.

    Returns:
        float: The calculated personnel capacity.

    """
    workdays = get_workdays(t)
    holidays = 2.5
    hours_per_day = 7.8
    try:
        pc = total_minutes / ((workdays - holidays) * hours_per_day * 60)
    except Exception as e:
        logging.error(f"Error calculating personnel capacity: {e}")
        pc = 0.0
    pc = round_up(pc, 4)
    return pc


def total_minutes_correspondence(
    t: datetime = datetime.now() - relativedelta(months=1),
) -> int:
    cnxn = get_db()
    try:
        cursor = cnxn.cursor()
        table_name = TABLES["Kunden Korrespondenz"] + t.strftime("_%Y")

        # Format t into a string that SQL Server can understand
        t_str = t.strftime("%d.%m.%Y")
        cursor.execute(
            f"SELECT Anzahl FROM {table_name} WHERE MONTH(Zeitstempel) = MONTH('{t_str}')"
        )
        tm_correspondence = cursor.fetchone()[0] * BZ
    except Exception as e:
        logging.error(f"Error retrieving total minutes for correspondence: {e}")
        tm_correspondence = 0

    cnxn.close()
    return tm_correspondence
