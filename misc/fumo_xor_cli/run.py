import sys
from random import randint
from time import sleep
from os import listdir, environ

key_list = []
frame_list = []
ANSI_CURSOR_UP = u'\u001b[A'
ANSI_RESET = u'\u001b[0m'

for file in listdir("gif"):
    with open("gif/"+file, "r") as fp:
        frame_list.append(fp.read())

for file in listdir("key"):
    with open("key/"+file, "r") as fp:
        key_list.append(fp.read())

def play_2_cli(frame_data, frame_time):
    sys.stdout.write(ANSI_CURSOR_UP * previous_line_count)
    sys.stdout.write(frame_data)
    sys.stdout.write('\n')
    sys.stdout.flush()
    sleep(frame_time)

i, key_count = 0, 0
try:
    frame_time = float(environ["FTIME"])
except KeyError:
    frame_time = 0.1
previous_line_count = len(frame_list[0].split('\n'))

while i < 3:

    for frame in frame_list:
        play_2_cli(frame, frame_time)
        if key_count < 2 and ((i > 0 and randint(0, 2) == 0) or (i == 3)):
            play_2_cli(key_list[key_count], frame_time)
            key_count += 1
    i += 1

sys.stdout.write(ANSI_RESET)
