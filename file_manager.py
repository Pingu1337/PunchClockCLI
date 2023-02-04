from colorama import Fore, Back, Style
from datetime import time, date, datetime, timedelta
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
            df.loc[index[0], 'on_pause'] = False
        else:
            h_method = 'punched in' if method == 'check_in' else 'punched out'
            Print(
                Fore.RED, f'You have already {h_method} today @ {Fore.LIGHTMAGENTA_EX}{df.loc[index[0], method]}{Style.RESET_ALL}')
            return False
    else:
        if method == 'check_out':
            Print(Fore.RED, "You haven't punched in today, can't punch out.")
            return False
        else:
            d = [{'date': today, method: time_data,
                  f'{method}:time_stamp': data, 'on_pause': False}]
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


def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


def pause():
    today = datetime.now().strftime('%y-%m-%d')
    create_outfile_if_not_exists()
    file = get_file()
    df = pd.read_csv(file)
    index = df.index[df['date'] == today].tolist()
    if len(index) > 0:
        if not df.loc[index[0], 'check_in']:
            Print(Fore.RED, "not punched in")
            return
        if df.loc[index[0], "on_pause"] == True:
            Print(Fore.RED, "already paused")
            return
        df.loc[index[0], "on_pause"] = True
        df.to_csv(file, index=False)
        f = open('pause.txt', 'w')
        f.write(str(datetime.now().timestamp()))
        f.close()
        Print(Fore.LIGHTCYAN_EX, f'pause: {Fore.GREEN}True')


def un_pause():
    today = datetime.now().strftime('%y-%m-%d')
    create_outfile_if_not_exists()
    file = get_file()
    df = pd.read_csv(file)
    index = df.index[df['date'] == today].tolist()
    if len(index) > 0:
        if not df.loc[index[0], 'check_in']:
            Print(Fore.RED, "not punched in")
            return
        if df.loc[index[0], "on_pause"] == False:
            Print(Fore.RED, "not paused")
            return
        f = open('pause.txt', 'r')
        time_stamp = f.read()
        break_time = datetime.fromtimestamp(float(time_stamp))
        delta = datetime.now() - break_time
        str_delta = strfdelta(delta, "{hours}:{minutes}:{seconds}")
        h = int(str_delta.split(':')[0])
        m = int(str_delta.split(':')[1])
        s = int(str_delta.split(':')[2])
        pasued_time = time(hour=h, minute=m, second=s)
        tot_pause = df.loc[index[0], "pause_time"]
        try:
            if math.isnan(tot_pause):
                df.loc[index[0], "pause_time"] = str_delta
        except:
            h = int(tot_pause.split(':')[0])
            m = int(tot_pause.split(':')[1])
            s = int(tot_pause.split(':')[2])
            tot_pause = timedelta(hours=h, minutes=m, seconds=s) + timedelta(
                hours=pasued_time.hour, minutes=pasued_time.minute, seconds=pasued_time.second)
            df.loc[index[0], "pause_time"] = tot_pause

        df.loc[index[0], "on_pause"] = False
        df.to_csv(file, index=False)

        Print(Fore.LIGHTCYAN_EX, f'pause: {Fore.RED}False')
        Print(Fore.LIGHTYELLOW_EX,
              f'was paused for {Fore.CYAN}{pasued_time}')


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
                  "check_out", "check_out:time_stamp", "on_pause", "pause_time"]
        f = open(file, 'w')
        writer = csv.writer(f)
        writer.writerow(header)
        f.close()
