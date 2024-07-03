from typing import Dict

import pyodbc

from utils import *
from database_interactions import *
from excel_interactions import *

file_names: Dict[str, str] = json.load(open("config.json", encoding="UTF-8"))[
    "FILE_NAMES"
]
input_dirs: Dict[str, str] = json.load(open("config.json", encoding="UTF-8"))[
    "INPUT_DIRS"
]

archive_dirs: Dict[str, str] = json.load(open("config.json", encoding="UTF-8"))[
    "ARCHIVE_DIRS"
]

sources = ["Mail Order", "Mail Service", "Kunden Korrespondenz", "VAK"]

if __name__ == "__main__":

    config_logging()
    t = datetime.now() - relativedelta(months=1)  # Timestamp

    logging.info("Starting file existence check...")
    check_file_existence(sources=sources, input_dirs=input_dirs, file_names=file_names)

    logging.info("Starting database preparations...")
    check_database_connection()
    create_correspondence(t)
    create_mail_order(t)
    create_mail_service(t)
    create_kpis(t)

    logging.info("Reading data from files...")
    month_missing_kpis = determine_missing_kpis(t)

    df_mail_order = read_mail_order(
        input_dirs["Mail Order"], file_names["Mail Order"], month_missing_kpis
    )
    df_mail_service = read_mail_service(
        input_dirs["Mail Service"], file_names["Mail Service"], month_missing_kpis
    )
    df_correspondence = read_correspondence(
        input_dirs["Kunden Korrespondenz"],
        file_names["Kunden Korrespondenz"],
        month_missing_kpis,
    )
    df_vak = read_vak(input_dirs["VAK"], file_names["VAK"], month_missing_kpis)

    available_months = available_data(
        df_mail_order, df_mail_service, df_correspondence, df_vak
    )

    logging.info("Computing KPIs...")
    update_month = list(set(available_months) & set(month_missing_kpis))
    if not update_month:
        logging.info("No data to update in the database.")
        exit(0)

    logging.info("Inserting data into database...")
    upsert_mail_order(t, df_mail_order, update_month)
    upsert_mail_service(t, df_mail_service, update_month)
    upsert_correspondence(t, df_correspondence, update_month)
    upsert_vak(t, df_vak, update_month)

    logging.info("Moving files to archive...")
    move_files(t, sources, input_dirs, archive_dirs, file_names)
    logging.info("Process completed successfully.")
