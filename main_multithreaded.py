from operator import itemgetter
import cv2
import numpy as np
import win32api

import time
from PIL import ImageGrab
import threading
from queue import Queue

crop_x = 631
crop_y = 458
crop_w = 395 + crop_x
crop_h = 255 + crop_y


def find_needle(queue, needle_uri, haystack):
    needle = cv2.imread(needle_uri)
    matches = []
    is_new_pt = False

    res = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        if matches:
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

    if matches:
        print("A thread found")
        print(matches)
        queue.put(matches)
    else:
        find_needle(queue, needle_uri, save_screencap())


def save_screencap():
    screenshot_pil = ImageGrab.grab()
    screenshot_pil_cropped = screenshot_pil.crop((crop_x, crop_y, crop_w, crop_h))
    screenshot_numpy = np.array(screenshot_pil_cropped.getdata(), dtype=np.uint8)\
        .reshape((screenshot_pil_cropped.size[1], screenshot_pil_cropped.size[0], 3))
    screenshot_pil_cropped.load()
    screenshot_pil_cropped.save("log/screencap.png")
    return screenshot_numpy


def main():
    screenshot = save_screencap()
    threads = []

    for n in needles:
        print("Starting thread")
        t = threading.Thread(target=find_needle, args=(q, n, screenshot))
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    match_tuples = q.get()
    print("gottem!")
    print(match_tuples)

    if match_tuples:
        print("found needles!")
        match_tuples = list(reversed(sorted(match_tuples, key=itemgetter(0))))
        print(match_tuples)
        win32api.SetCursorPos((match_tuples[0][0] + crop_x + 20, match_tuples[0][1] + crop_y))
    else:
        print("found no matches")


needles = ["imgs/particle1.png", "imgs/particle2.png", "imgs/particle3.png", "imgs/particle4.png"]

q = Queue()

# main()

while True:
    main()
    time.sleep(0.5)
    if win32api.GetAsyncKeyState(222):
        break
