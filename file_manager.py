from colorama import Fore, Back, Style
from datetime import time, date, datetime
import math
import pandas as pd
import json
import csv
import os


def Print(color, msg):
    print(color + msg + Style.RESET_ALL)


def set_file(args):
    if len(args) <= 1:
        Print(Fore.RED, 'argument "file_name" is required')
        return

    file_name = args[1]

    file_exists = os.path.isfile('meta.json')
    if not file_exists:
        create_meta()

    f = open('meta.json', 'r+')
    data = json.load(f)
    data['out_file'] = file_name

    f.seek(0)
    json.dump(data, f, indent=4)

    create_outfile_if_not_exists()

    Print(Fore.LIGHTMAGENTA_EX, 'data will now be saved to ' +
          Fore.LIGHTYELLOW_EX + args[1])


def get_file():
    f = open('meta.json', 'r')
    data = json.load(f)
    return data['out_file']


def save_data(data, method):
    file_exists = os.path.isfile('meta.json')
    if not file_exists:
        create_meta()
    create_outfile_if_not_exists()

    today = datetime.fromtimestamp(data).strftime("%y-%m-%d")
    time_data = datetime.fromtimestamp(data).strftime("%H:%M:%S")
    file = get_file()
    df = pd.read_csv(file)
    index = df.index[df['date'] == today].tolist()

    if len(index) > 0:
        if not df.loc[index[0], method] or math.isnan(float(df.loc[index[0], method+':time_stamp'])):
            df.loc[index[0], method] = time_data
            df.loc[index[0], method+':time_stamp'] = data
        else:
            h_method = 'checked in' if method == 'check_in' else 'checked out'
            Print(
                Fore.RED, f'You have already {h_method} today @ {Fore.LIGHTMAGENTA_EX}{df.loc[index[0], method]}{Style.RESET_ALL}')
            return False
    else:
        if method == 'check_out':
            Print(Fore.RED, "You haven't checked in today, can't check out.")
            return False
        else:
            d = [{'date': today, method: time_data,
                  f'{method}:time_stamp': data}]
            a_df = pd.DataFrame(d)
            df = pd.concat([df, a_df], ignore_index=True).drop_duplicates()

    df.to_csv(file, index=False)
    return True


def read_data(today):
    create_outfile_if_not_exists()
    file = get_file()
    df = pd.read_csv(file)
    index = df.index[df['date'] == today].tolist()
    if len(index) > 0:
        return df.loc[index[0]]
    else:
        return range(0)


def create_meta():
    f = open('meta.json', 'w')
    json_data = {
        "out_file": "output.scv"
    }
    json.dump(json_data, f, indent=4)
    f.close()


def create_outfile_if_not_exists():
    file = get_file()
    file_exists = os.path.isfile(file)
    if not file_exists:
        header = ["date", "check_in", "check_in:time_stamp",
                  "check_out", "check_out:time_stamp"]
        f = open(file, 'w')
        writer = csv.writer(f)
        writer.writerow(header)
        f.close()
