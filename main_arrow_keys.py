# INFO: This version does not currently work (at least definitely not when run from an IDE)
#       because the button triggers aren't recognised by STO
from operator import itemgetter

import cv2
import numpy as np
import win32api

import time
from PIL import ImageGrab
import threading
from queue import Queue

from KeyHelper import SendInput, Keyboard, VK_UP, VK_DOWN

# Crop constants may very, I measured them using a screenshot of my game running in fullscreen at 1920x1080
crop_x = 631
crop_y = 458
crop_w = 395 + crop_x
crop_h = 255 + crop_y

column_1 = {'id': 1, 'top': 15, 'bottom': 60}
column_2 = {'id': 2, 'top': 75, 'bottom': 120}
column_3 = {'id': 3, 'top': 135, 'bottom': 180}
column_4 = {'id': 4, 'top': 195, 'bottom': 240}

columns = [column_1, column_2, column_3, column_4]

curr_column = 1

cursor_x = crop_x + crop_w - 665

# Global variable used to keep track of how many threads are finished with their search
threads_finished = 0


# Takes an image(needle) and another one to search it in(haystack) and puts results in the queue
def find_needle(queue, needle_uri, haystack):
    needle = cv2.imread(needle_uri)
    matches = []
    is_new_pt = False

    # Compare images
    res = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
    threshold = .6
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        if matches:
            # Iterate through matches and see if their duplicates or if they are new and get added to the results
            for match in matches:
                if match[0] - 2 <= pt[0] <= match[0] + 2 and match[1] - 2 <= pt[1] <= match[1] + 2:
                    is_new_pt = False
                    break
                else:
                    is_new_pt = True
            if is_new_pt:
                matches.append(pt)
        else:
            matches.append(pt)

    # Adds 1 to threads_finished and puts results in the queue
    print(matches)
    global threads_finished
    threads_finished += 1
    print(str(threads_finished) + " out of 4 threads finished!")
    queue.put(matches)


# Captures current screen, crops it to save time in find_needle later on and converts it to a numpy array
def save_screencap():
    screenshot_pil = ImageGrab.grab()
    screenshot_pil_cropped = screenshot_pil.crop((crop_x, crop_y, crop_w, crop_h))
    screenshot_numpy = np.array(screenshot_pil_cropped.getdata(), dtype=np.uint8) \
        .reshape((screenshot_pil_cropped.size[1], screenshot_pil_cropped.size[0], 3))
    return screenshot_numpy


# The main function. Creates threads, collects and evaluates results and virtually triggers arrow keys
def main():
    global threads_finished
    global curr_column
    screenshot = save_screencap()
    for n in needles:
        print("Starting thread")
        t = threading.Thread(target=find_needle, args=(q, n, screenshot))
        t.daemon = True
        t.start()

    match_tuples = []
    # Collect results from threads and only move on when all 4 are finished
    # necessary to evaluate results from all threads(e.g. all needles)
    while threads_finished < 4:
        for match in q.get():
            match_tuples.append(match)

    print("gottem all!")
    print(match_tuples)

    # if matches were found, order them by x value, check in what column the most right one is
    # and trigger arrow keys accordingly
    if match_tuples:
        print("found needles!")
        match_tuples = list(reversed(sorted(match_tuples, key=itemgetter(0))))
        target_x, target_y = match_tuples[0]
        print(match_tuples)
        for column in columns:
            if column["top"] <= target_y <= column["bottom"]:
                print("Found target column:" + str(column["id"]))
                difference = curr_column - column["id"]
                if difference < 0:
                    for i in range(0, abs(difference)):
                        SendInput(Keyboard(VK_DOWN))
                else:
                    for i in range(0, abs(difference)):
                        SendInput(Keyboard(VK_UP))
                curr_column = column["id"]
        print("Moved column!")
    else:
        print("found no matches")

    # if user doesn't abort by pressing key 222 (ä), commence new search
    if not win32api.GetAsyncKeyState(222):
        threads_finished = 0
        main()


# The needles(images) to find in the haystack(larger image)
needles = ["imgs\particle1.png", "imgs\particle2.png",
           "imgs\particle3.png", "imgs\particle4.png"]

q = Queue()

# start when user presses key 192 (ö)
while not win32api.GetAsyncKeyState(192):
    time.sleep(0.5)

main()

