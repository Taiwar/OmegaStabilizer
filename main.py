from operator import itemgetter

import cv2
import numpy as np
import win32api
from PIL import ImageGrab


def find_needle(needle_uri, haystack):
    needle = cv2.imread(needle_uri)
    # w, h = needle.shape[:-1]
    matches = []
    is_new_pt = False

    res = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        # cv2.rectangle(haystack, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        matches.append(pt)
        if matches:
            for match in matches:
                if match[0]-2 <= pt[0] <= match[0]+2 and match[1]-2 <= pt[1] <= match[1]+2:
                    is_new_pt = False
                    break
                else:
                    is_new_pt = True
            if is_new_pt:
                print("found new pt:")
                print(pt)
                matches.append(pt)
        else:
            print("found new pt:")
            print(pt)
            matches.append(pt)
    return matches


def save_screencap():
    screenshot_pil = ImageGrab.grab()
    screenshot_numpy = np.array(screenshot_pil.getdata(), dtype=np.uint8)\
        .reshape((screenshot_pil.size[1], screenshot_pil.size[0], 3))
    return screenshot_numpy
    # screenshot.load()
    # screenshot.save("log/screencap.png")


def main():
    screencap = save_screencap()
    match_tuples = []
    for i in range(1, 5):
        matches = find_needle("imgs/particle" + str(i) + ".png", screencap)
        if matches:
            for match in matches:
                match_tuples.append(match)
    if match_tuples:
        match_tuples = list(reversed(sorted(match_tuples, key=itemgetter(0))))
        print(match_tuples)
        win32api.SetCursorPos(match_tuples[0])
    else:
        print("found no matches")

while True:
    while win32api.GetAsyncKeyState(222):
        main()
