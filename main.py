from operator import itemgetter
from random import randint

import cv2
import numpy as np
import win32api

import time
from PIL import ImageGrab
import threading
from queue import Queue

# Crop constants may very, I measured them using a screenshot of my game running in fullscreen at 1920x1080
crop_x = 850
crop_y = 458
crop_w = 115 + crop_x
crop_h = 255 + crop_y

# Position to put the cursor at
cursor_x = crop_x + crop_w - 800

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
                if match[0]-2 <= pt[0] <= match[0]+2 and match[1]-2 <= pt[1] <= match[1]+2:
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


# The main function. Creates threads, collects and evaluates results and moves mouse cursor
def main():
    global threads_finished
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

    # if matches were found, order them by x value
    # and move cursor to y-coords of the first match (e.g. the one most to the right)
    if match_tuples:
        print("found needles!")
        match_tuples = list(reversed(sorted(match_tuples, key=itemgetter(0))))
        target_x, target_y = match_tuples[0]
        print(match_tuples)
        current_cursor_x, current_cursor_y = win32api.GetCursorPos()  # Get current cursor position
        breaker = 0
        # Gradually move mouse to appropriate y-coords and randomise x-coords a bit so the movement gets recognized
        while not (target_y + crop_y - 5) <= current_cursor_y <= (target_y + crop_y + 5):
            print(str(current_cursor_y) + " is not within the range: (" + str(target_y + crop_y - 5) + ", " +
                  str(target_y + crop_y + 5) + ")")
            # emergency break to allow for detection of abort key if smth goes wrong
            if breaker > 100:
                break
            rand_x = randint(0, 20)
            # check if current cursor y-pos is greater or lower than target y and move accordingly
            if current_cursor_y > (target_y + crop_y):
                win32api.SetCursorPos((cursor_x + rand_x, current_cursor_y - 10))
            else:
                win32api.SetCursorPos((cursor_x + rand_x, current_cursor_y + 10))
            time.sleep(0.01)
            breaker += 1
            current_cursor_x, current_cursor_y = win32api.GetCursorPos()
        print("Moved cursor!")
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

main()

