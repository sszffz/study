"""
log information
"""
import os
import logging

import logging.handlers
import os
from datetime import datetime

from security import pathinfo

handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", pathinfo.get_log_file_path()))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)


def log(text: str):
    # datetime object containing current date and time
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    logging.log(logging.INFO, "{}: {}".format(dt_string, text))
