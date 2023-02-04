import textwrap
from colorama import Fore, Back, Style
import argparse
from datetime import time, date, datetime
import file_manager
import math


def Print(color, msg):
    print(color + msg + Style.RESET_ALL)


def test(args):
    if len(args) <= 1:
        Print(Fore.RED, 'argument "message" is required')
        return
    Print(Fore.LIGHTMAGENTA_EX, 'You Entered: ' +
          Fore.LIGHTYELLOW_EX + args[1])


def check_in():
    now = datetime.now()
    time_stamp = datetime.timestamp(now)
    noerr = file_manager.save_data(time_stamp, 'check_in')
    if not noerr:
        return
    t = now.strftime("%H:%M:%S")
    Print(Fore.LIGHTGREEN_EX,
          f'Punched In @ {Fore.LIGHTMAGENTA_EX + t}')


def check_out():
    now = datetime.now()
    time_stamp = datetime.timestamp(now)
    noerr = file_manager.save_data(time_stamp, 'check_out')
    if not noerr:
        return
    t = now.strftime("%H:%M:%S")
    Print(Fore.LIGHTRED_EX,
          f'Punched Out @ {Fore.LIGHTMAGENTA_EX + t}')


def get_status():
    today = datetime.now().strftime('%y-%m-%d')
    data = file_manager.read_data(today)
    status = 'not checked in'
    if not len(data) > 0:
        Print(Fore.LIGHTMAGENTA_EX, status)
        return
    if not math.isnan(float(data['check_in:time_stamp'])):
        status = f'punched in @ {Fore.LIGHTCYAN_EX + data["check_in"]}'
    if not math.isnan(float(data['check_out:time_stamp'])):
        status = f'punched out @ {Fore.LIGHTCYAN_EX + data["check_out"]}'
    Print(Fore.LIGHTMAGENTA_EX, status)


commands = {
    "in": {'func': check_in, 'args': 0},
    "out": {'func': check_out, 'args': 0},
    "file": {'func': file_manager.set_file, 'args': 1},
    "status": {'func': get_status, 'args': 0},
    "pause": {'func': file_manager.pause, 'args': 0},
    "unpause": {'func': file_manager.un_pause, 'args': 0},
    "test": {'func': test, 'args': 1}
}


def main():
    parser = argparse.ArgumentParser(
        prog='punch', formatter_class=argparse.RawTextHelpFormatter, description="A cli punch clock")

    # defining arguments for parser object
    # parser.add_argument("cmd", type=str)
    # parser.add_argument(
    #     "-h", "--help", action="custom_help", help="show this help message")

    parser.add_argument("cmd", type=str, nargs='*',
                        metavar='command',
                        help="in \t punch in \nout \t punch out \npause \t go on break \nunpause \t back from break\nstatus \t get current status' \nfile \t set output file path/name e.g \"punch file ~/work_hours.csv\"")

    parser.add_argument("-o", "--output", default=None, help='set output file',
                        metavar='file_name')

    args = parser.parse_args()

    Print(Fore.YELLOW, f'DEBUG: {Fore.YELLOW}{args}')
    if args.output != None:
        file_manager.set_file(['-', args.output])
    if commands[args.cmd[0]]['args'] < 1:
        commands[args.cmd[0]]['func']()
    else:
        commands[args.cmd[0]]['func'](args.cmd)


if __name__ == "__main__":
    # calling the main function
    main()
