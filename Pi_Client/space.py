#! /usr/bin/python

import freenect
import frame_convert

THRESHOLD=254

def get_depth():
    return frame_convert.pretty_depth(freenect.sync_get_depth()[0])

def to_len(ar):
    for x in range(1, len(ar)-1):
        ar[x] = ar[x-1] * ar[x] + ar[x]
    return ar
        
def max_run(ar):
    max = i = pos = 0
    for x in ar:
        i += 1
        if x > max:
            max = x
            pos = i
    return pos - max / 2


while True:
    x = get_depth()[200]
    y = map (lambda x : 1 if x < 200 else 0, x)
    print " " * (max_run(to_len(y)) / 10) + "#"

