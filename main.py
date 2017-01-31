from operator import itemgetter

import cv2
import numpy as np
import win32api
from PIL import ImageGrab


def find_needle(needle_uri, haystack):
    print("searching for: " + needle_uri)
    needle = cv2.imread(needle_uri)
    w, h = needle.shape[:-1]
    matches = []

    res = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        print("got pt")
        cv2.rectangle(haystack, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        cv2.imwrite('imgs/result' + needle_uri[:-4] + '.png', haystack)
        matches.append(pt)
        if matches:
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
