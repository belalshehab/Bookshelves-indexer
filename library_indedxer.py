import numpy as np

from image_segmenter import ImageSegmenter, Orientation
from book import Book

import cv2 as cv

import json


class LibraryIndexer:
    def __init__(self, image, config=None):
        self.__config = config
        if config is None:
            with open('config.json', 'r') as f:
                self.__config = json.load(f)

        self.__image = image
        self.__shelves = []
        self.__spines = []

        self.__books = []

    def __extract_shelves(self, image):
        shelves_segmenter = ImageSegmenter(image, Orientation.HORIZONTAL, self.__config.get('shelves_segmenter'),
                                           debug=False)
        shelves_segmenter.extract_segments()
        return shelves_segmenter.get_segments_with_coordinates()

    def __extract_spines(self, shelf):
        spines_segmenter = ImageSegmenter(shelf, Orientation.VERTICAL, self.__config.get('spines_segmenter'),
                                          debug=False)
        spines_segmenter.extract_segments()
        return spines_segmenter.get_segments_with_coordinates()

    def extract_books(self):
        self.__books.clear()
        shelves = self.__extract_shelves(self.__image)
        for shelf_index, shelf in enumerate(shelves):
            shelf_lower_point = shelf[1]
            shelf_upper_point = shelf[2]
            shelf = shelf[0]
            spines = self.__extract_spines(shelf)
            for spine_index, spine in enumerate(spines):
                spine_lower_point = spine[1]
                spine_upper_point = spine[2]
                spine = spine[0]
                book = {
                    'spine': spine,
                    'shelf': shelf_index,
                    'index': spine_index,
                    'bounding_rectangle': ((spine_lower_point, shelf_lower_point),
                                           (spine_upper_point, shelf_upper_point))
                }
                self.__books.append(book)
        return self.__books

    def get_books(self):
        return self.__books


if __name__ == '__main__':
    path = 'images/maktaba/01.jpg'
    library = cv.imread(path)
    library_copy = np.copy(library)
    library_indexer = LibraryIndexer(library)
    books = library_indexer.extract_books()

    for book in books:
        p0 = book.get("bounding_rectangle")[0]
        p1 = book.get("bounding_rectangle")[1]
        print(f'book: {book.get("shelf")}, {book.get("index")}, {book.get("bounding_rectangle")}')
        cv.imshow(f'{book.get("shelf")}_{book.get("index")}', book.get('spine'))
        cv.rectangle(library_copy, p0, p1, (0, 255, 255), 3)
        center = (int((p0[0] + p1[0]) / 2), int((p0[1] + p1[1]) / 2))
        print(center)
        cv.putText(library_copy, f'{book.get("shelf")}_{book.get("index")}',
                   center, cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv.imshow(f'library', library_copy)
    cv.waitKey(0)
