import numpy as np

from image_segmenter import ImageSegmenter, Orientation
from book import Book
from info_extractor import InfoExtractor

import cv2 as cv

import json


class LibraryIndexer:
    def __init__(self, library_image, config=None):
        self.__config = config
        if config is None:
            with open('config.json', 'r') as f:
                self.__config = json.load(f)
        self.__library_image = library_image
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
        shelves = self.__extract_shelves(self.__library_image)
        for shelf_index, shelf in enumerate(shelves):
            shelf_lower_point = shelf[1]
            shelf_upper_point = shelf[2]
            shelf = shelf[0]
            spines = self.__extract_spines(shelf)
            for spine_index, spine in enumerate(spines):
                spine_lower_point = spine[1]
                spine_upper_point = spine[2]
                spine = spine[0]
                book = Book()
                book.spine = spine
                book.shelf = shelf_index
                book.index = spine_index
                book.bounding_rectangle = ((spine_lower_point, shelf_lower_point),
                                           (spine_upper_point, shelf_upper_point))
                self.__books.append(book)
        return self.__books

    def extract_books_info(self):
        for index, book in enumerate(self.__books):
            progress = round(index / len(self.__books), 2)
            print(f'prog: {progress}')
            infoExtractor = InfoExtractor(book.spine, book)
            self.__books[index] = infoExtractor.extract_book_info()
        return self.__books

    def get_books(self):
        return self.__books


def indexer_wrapper(path):
    with open('./config.json', 'r') as f:
        config = json.load(f)
    library = cv.imread(path)
    library_indexer = LibraryIndexer(library, config)
    books = library_indexer.extract_books()
    books = library_indexer.extract_books_info()
    return books


def spot_the_book(book):
    image = cv.imread(book['library_url'])
    p0 = book['bounding_rectangle'][0]
    p1 = book['bounding_rectangle'][1]
    cv.rectangle(image, p0, p1, (255, 0, 255), 3)
    cv.imwrite('./static/tmp.png', image)
    book['library_url'] = './static/tmp.png'
    return book


if __name__ == '__main__':
    path = 'images/maktaba/04.jpg'
    library = cv.imread(path)
    library_copy = np.copy(library)

    library_indexer = LibraryIndexer(library)
    library_indexer.extract_books()
    books = library_indexer.extract_books_info()

    for book in books:
        p0 = book.bounding_rectangle[0]
        p1 = book.bounding_rectangle[1]
        print(book)
        # cv.imshow(f'{book.shelf}_{book.index}', book.spine)
        cv.rectangle(library_copy, p0, p1, (0, 255, 255), 3)
        center = (int((p0[0] + p1[0]) / 2), int((p0[1] + p1[1]) / 2))
        print(center)
        cv.putText(library_copy, f'{book.shelf}_{book.index}', center, cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv.imshow(f'library', library_copy)
    cv.waitKey(0)
