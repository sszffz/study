"""
log information
"""
import os
import logging

import logging.handlers
import os
import sys
from datetime import datetime

from security.config import config

handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", config.path.log_file_path))
stdout_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)
root.addHandler(stdout_handler)

# file_handler = logging.FileHandler(filename=config.path.log_file_path)
# stdout_handler = logging.StreamHandler(sys.stdout)
# handlers = [file_handler, stdout_handler]

# logging.basicConfig(
#     level=logging.INFO,
#     format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
#     handlers=handlers
# )


def log(text: str):
    # datetime object containing current date and time
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    logging.log(logging.INFO, "{}: {}".format(dt_string, text))
