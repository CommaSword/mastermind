#!/usr/bin/env python3

"""
Load- Load Utility X to Chip Y

Show - Shows the current loadout

Execute - running the loadout and getting the feedback
"""
import sys
import os
import math
import string
import random
from time import sleep
from ctypes import windll
from urllib import request
from urllib.error import URLError
import importlib.util
from typing import List, Dict, Tuple
from types import ModuleType

if os.name == 'nt':
    os.system('cls')  # For Windows
else:
    os.system('clear')  # For Linux/OS X


COMMANDS_HEADER = """
##################################################
##                                              ##
##                   COMMANDS                   ##
##                                              ##
##################################################
##                                              ##
##               load utilX chipY               ##
##                    execute                   ##
##                    commands                  ##
##                  show phases                 ##
##                   show chips                 ##
##                 show utilities               ##
##                                              ##
##################################################
##################################################
"""

HISTORY_FORMAT = """
##################################################
##                                              ##
##                   PHASE {phase}                   ##
##                                              ##
##                   SEQUENCE                   ##
##                                              ##
{sequence}
##                                              ##
##                    HINTS                     ##
##                                              ##
{hints}
##################################################
"""


# locate config
def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives


def locate_config() -> str:
    config_path = ""
    for drive in get_drives():
        if os.path.exists(drive + ":/mastermind_config.py"):
            config_path = drive + ":/mastermind_config.py"
    return config_path


def load_config(config_path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location("module.name", config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules['conf'] = module
    return module


def successful_termination():
    fakeCode(3, "PROGRAM TERMINATED.\n",
             ["terminating", "deactivating", "unloading", "deallocation of", "unhooking", "closing"])
    sleep(1)
    sys.exit()


def failed_termination():
    print("\nERROR! REPAIR ATTEMPTS EXCEEDED.\n")
    sleep(3)
    fakeCode(4, "PROGRAM TERMINATED.",
             ["terminating", "deactivating", "unloading", "deallocation of", "unhooking", "closing"])
    sleep(1)
    sys.exit()


def send_request(url: str) -> None:
    print("transmitting data to server...\n")
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://{}'.format(url)
    for i in range(8):
        print("sending...\n")
        sleep(1)
        try:
            res = request.urlopen(url)
        except URLError:
            print('Failed transmitting to server. Retrying')
            continue
        if res.status == 200:
            print("transmission complete.")
            sleep(1)
            return
        else:
            continue
    print("error transmitting data to server.")
    sleep(1)


def fakeCode(l, message, actions):
    letters = string.ascii_lowercase + string.ascii_uppercase
    keyphrases = ["transmission...", "radial controls...", "ciphers...", "phases...", "chips...", "utilities..."]
    strings = ""
    r = ["\n".join(["".join([random.choice(letters) for i in range(50)]) for x in range(random.randint(1, 5))]) for o in
         range(l)]
    for i in r:
        strings = strings + "\n" + "\n".join([random.choice(actions) + " " + random.choice(keyphrases) for i in
                                              range(random.randint(1, 3))]) + "\n\n" + i + "\n"
        strings = strings + " ".join(
            ["0x" + "".join([str(random.randint(0, 9)) for x in range(2)]) for o in range(10)]) + str(
            random.randint(0, 9)) + "\n"
        strings = strings + " ".join(
            ["0x" + "".join([str(random.randint(0, 9)) for x in range(2)]) for o in range(10)]) + str(
            random.randint(0, 9)) + "\n"
    strings = strings + "\n" + "\n".join([random.choice(actions) + " " + random.choice(keyphrases) for i in
                                          range(random.randint(1, 3))]) + "\n\n" + i + "\n"
    strings = strings + ("\n%s\n" % message)
    index = 0
    while index < len(strings):
        offset = random.randint(1, 3)
        print(strings[index:index + offset], end='')
        index = index + offset
        sleep(float(random.randint(1, 5)) / 500)


def compare(code: List[str], sequence: List[str]) -> Tuple[bool, Dict[str, int]]:
    # If sequence matches - return True and exit. Otherwise continue
    if code == sequence:
        return True, {}
    # Sequence does not match. Calculate hints.
    hints = {}
    effective = [True if sequence[i] == code[i] else False for i in range(len(code))]
    hints['effective'] = effective.count(True)
    hints['effective on another chip'] = \
        [
            True if not effective[i] and
            sequence[i] in code and
            code.count(sequence[i]) >= sequence[:i].count(sequence[i]) else False
            for i in range(len(code))
        ].count(True)
    return False, hints


def show(conf: ModuleType) -> None:
    for index, b in enumerate(conf.BOARD):
        chips = " ".join(["%s:%s" % (conf.CHIPS[i], b["sequence"][i]) for i in range(conf.N_CHIPS)])
        seq = "##{}{}{}##"\
            .format(" " * int(math.ceil((46 - len(chips)) / 2)), chips, " " * int(math.floor((46 - len(chips)) / 2)))
        hints = b["hints"]
        if not any(hints.values()):
            f_hints = ["##             no feedback available.           ##"]
        else:
            f_hints = []
            for key, value in hints.items():
                inner = "{} {} {}".format(value, 'utility' if value == 1 else 'utilities', key)
                f_hints.append("##{}{}{}##"
                               .format(" " * int(math.ceil((46 - len(inner)) / 2)),
                                       inner,
                                       " " * int(math.floor((46 - len(inner)) / 2))))
        print(HISTORY_FORMAT.format(phase=str(index + 1).ljust(2),
                                    sequence=seq,
                                    hints='\n'.join(f_hints)))


def load(util_name: str, chip_name: str, utilities: List[str], chips: List[str],
         sequence: List[str]) -> Tuple[bool, str]:
    # errors
    if util_name not in utilities:
        return False, "utility must be valid: {}".format(', '.join(utilities))
    if chip_name not in chips:
        return False, "chip must be valid: {}".format(', '.join(chips))

    chip_n = chips.index(chip_name)
    sequence[chip_n] = util_name
    return True, "loaded %s into %s." % (util_name, chip_name)


def commands():
    print(COMMANDS_HEADER)


def print_hints(hints: Dict[str, int]) -> None:
    if not any(hints.values()):
        print("no feedback available.")
        return
    for key, count in hints.items():
        print('{} {} {}'.format(count, 'utility' if count == 1 else 'utilities', key))


def pregame():
    fakeCode(10, "PROGRAM INITIATED.",
             ["testing", "activating", "opening", "allocating", "hooking", "creating", "notifying", "enhancing",
              "signalling"])
    commands()


def loading(pre, post, load_time):
    for i in range(21):
        sys.stdout.write('\r')
        sys.stdout.write("%s%s" % (pre, " " * 5))
        # the exact output you're looking for:
        sys.stdout.write("[%-20s] %d%%" % ('=' * i, 5 * i))
        sys.stdout.flush()
        sleep(load_time)
    sys.stdout.write('\r')
    sys.stdout.write(post + " " * 50)
    print()


def main():
    pregame()
    conf_file = locate_config()
    if not conf_file:
        fakeCode(2, "ERROR! NO CHIPS OR UTILITIES DETECTED. PROGRAM TERMINATED.\n",
                 ["searching for ", "seeking", "locating", "hosting", "connecting", "finding", "making", "building"])
        sleep(3)
        sys.exit()
    conf = load_config(conf_file)
    # conf = load_config('/Users/yuvalm/projects/CommaSword/mastermind/mastermind_config.py')
    sequence = ["_" for _ in range(conf.N_CHIPS)]
    # for each turn while unsolved try again
    turn = 0
    while turn < conf.N_TURNS:

        # loop until valid input for turn
        command_passed = False
        while not command_passed:
            command_passed = True
            chips = " ".join(["%s:%s" % (conf.CHIPS[i], sequence[i]) for i in range(conf.N_CHIPS)])
            command = input('phase {}{} [ {} ]: '
                            .format(turn + 1,
                                    '' if turn != conf.N_TURNS - 1 else ' (final phase) ',
                                    chips)).split(' ')

            # parse command: LOAD
            if len(command) == 3 and command[0].lower() == "load" and command[1] in conf.UTILITIES \
                    and command[2] in conf.CHIPS:
                r, message = load(command[1], command[2], conf.UTILITIES, conf.CHIPS, sequence)
                print(message)
            elif len(command) == 2 and command[0].lower() == "show" and command[1].lower() in "phases":
                show(conf)
            elif len(command) == 2 and command[0].lower() == "show" and command[1].lower() in "chips":
                print("valid chips: %s" % ", ".join(conf.CHIPS))
            elif len(command) == 2 and command[0].lower() == "show" and command[1].lower() in "utilities":
                print("valid utilities: {}".format(", ".join(conf.UTILITIES)))
            elif "".join(command).lower() == "commands":
                commands()
            elif "".join(command).lower() == "execute":
                # increment turn
                turn += 1
                # check if SEQUENCE is correct
                r, hints = compare(conf.CODE, sequence)
                conf.BOARD.append({
                    "sequence": sequence,
                    "hints": hints
                })
                sequence = ["_" for _ in range(conf.N_CHIPS)]
                if r:
                    loading("executing...", "repaired.", conf.LOAD_TIME)
                    sleep(1)
                    send_request(conf.HTTP_URL)
                    sleep(3)
                    successful_termination()

                loading("executing...", "unable to repair.", conf.LOAD_TIME)

                # show hints for most recent sequence
                print_hints(hints)

            else:
                print("invalid command.")
                command_passed = False
    sleep(1)
    failed_termination()


if __name__ == '__main__':
    main()
