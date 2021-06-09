import cv2 as cv

from book import Book


class InfoExtractor:
    def __init__(self, image, book_info=None):
        """
        ocr detection
        and search goodreads
        """
        self.__image = image
        self.__book_info = book_info if book_info is not None else Book()

    def __ocr(self):
        """
        ocr operation
        """
        ocr_output = ''

        self.__book_info.ocr_output = ocr_output

    def __goodreads_search(self):
        """
        search book name by the ocr output
        """
        name = ''
        self.__book_info.name = name

    def extract_book_info(self):
        self.__ocr()
        self.__goodreads_search()

    def get_book_info(self):
        return self.__book_info


if __name__ == '__main__':
    path = 'images/output/spine_3.6.png'
    image = cv.imread(path)

    info_extractor = InfoExtractor(image)

    info_extractor.extract_book_info()
    info = info_extractor.get_book_info()

    print(info.name)
    print(info.ocr_output)
