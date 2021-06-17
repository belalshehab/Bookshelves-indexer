from library_indedxer import LibraryIndexer

import cv2 as cv
import numpy as np

import json


def empty(a):
    pass


def indexer(config, i):
    path = f'images/maktaba/0{i}.jpg'
    library = cv.imread(path)
    library_copy = np.copy(library)
    library_indexer = LibraryIndexer(library, config)
    books = library_indexer.extract_books()
    for book in books:
        p0 = book.bounding_rectangle[0]
        p1 = book.bounding_rectangle[1]
        # cv.imshow(f'{book.shelf}_{book.index}', book.spine)
        cv.rectangle(library_copy, p0, p1, (0, 255, 255), 3)
        center = (int((p0[0] + p1[0]) / 2), int((p0[1] + p1[1]) / 2))
        cv.putText(library_copy, f'{book.shelf}_{book.index}', center, cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv.imshow(f'library', library_copy)
    # cv.waitKey(0)


with open('config.json', 'r') as f:
    config = json.load(f)

cv.namedWindow("TrackBars")
cv.resizeWindow("TrackBars", 1000, 350)
cv.createTrackbar("minimum_length", "TrackBars", int(config['spines_segmenter']['minimum_length'] * 1000), 100, empty)
cv.createTrackbar("minimum_strength", "TrackBars", int(config['spines_segmenter']['minimum_strength'] * 100), 200, empty)
cv.createTrackbar("boundaries_offset", "TrackBars", int(config['spines_segmenter']['boundaries_offset'] * 1000), 100, empty)
cv.createTrackbar("neighbours_distance", "TrackBars", int(config['spines_segmenter']['neighbours_distance'] * 1000), 200, empty)
cv.createTrackbar("angle_margin", "TrackBars", int(config['spines_segmenter']['angle_margin'] * 100), 100, empty)

cv.createTrackbar("Hough_threshold", "TrackBars", int(config['spines_segmenter']['Hough_threshold']), 199, empty)
cv.createTrackbar("Hough_max_line_gap", "TrackBars", int(config['spines_segmenter']['Hough_max_line_gap']), 20, empty)

i = 1
while True:

    config['spines_segmenter']['minimum_length'] = cv.getTrackbarPos("minimum_length", "TrackBars") / 1000
    config['spines_segmenter']['minimum_strength'] = cv.getTrackbarPos("minimum_strength", "TrackBars") / 100
    config['spines_segmenter']['boundaries_offset'] = cv.getTrackbarPos("boundaries_offset", "TrackBars") / 1000
    config['spines_segmenter']['neighbours_distance'] = cv.getTrackbarPos("neighbours_distance", "TrackBars") / 1000
    config['spines_segmenter']['angle_margin'] = cv.getTrackbarPos("angle_margin", "TrackBars") / 100
    config['spines_segmenter']['Hough_threshold'] = cv.getTrackbarPos("Hough_threshold", "TrackBars")
    config['spines_segmenter']['Hough_max_line_gap'] = cv.getTrackbarPos("Hough_max_line_gap", "TrackBars")

    print(json.dumps(config['spines_segmenter']))
    indexer(config, i)

    if cv.waitKey(10) & 0xFF == ord('n'):
        i += 1
