"""
Download stock history from all companies

Change fix_yahoo_finance\_init_.py, in method "history", change
    "raise ValueError(error["description"])"
to
    return None.
Then we can tell whether history is downloaded or not, instead of interrupt the
downloading for other symbols.

GitHub Test
"""

import os
import pandas as pd
import fix_yahoo_finance as yf

# root_dir = r"C:\Users\ffz\PycharmProjects\stock\data"
root_dir = r"D:\MLData\PlayArea\stk\orig"
history_path = os.path.join(root_dir, "history")
company_list_path = os.path.join(root_dir, "companylist.csv")
finished_list_path = os.path.join(root_dir, "finishedList.txt")

company_list = pd.read_csv(company_list_path)
company_symbol_list = company_list["Symbol"]

finishedList = []
if os.path.isfile(finished_list_path):
    for line in open(finished_list_path, "r+").readlines():
        finishedList.append(line.strip())

proc_symbol_list = set(company_symbol_list) - set(finishedList)

for symbol in proc_symbol_list:
    with open("finishedList.txt", "a+") as f:
        f.write(symbol+"\n")

    try:
        print("downloading {}".format(symbol))
        data = yf.download(symbol, period="max")
        if data is not None:
            data.to_csv(os.path.join(history_path, symbol+".csv"))
    except:
        pass

