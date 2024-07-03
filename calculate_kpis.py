from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta
import holidays
import numpy as np


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


def personnel_cap(
    total_minutes: float, t: datetime = datetime.now() - relativedelta(months=1)
) -> float:
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
