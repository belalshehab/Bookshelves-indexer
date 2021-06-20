import cv2 as cv
import numpy
import numpy as np

from googlesearch import search
from book import Book
import pytesseract


# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def bookname_search(text):
    goodreads_url_prefix = "https://www.goodreads.com/book/show/"
    gen = search(text + " " + goodreads_url_prefix, tld='com', lang='en', num=1, pause=4)
    bookName_search_url = next(gen)

    index = bookName_search_url.find("show/") + len('show/')

    book_name = bookName_search_url[index:]

    book_name = book_name.replace("-", " ").replace("_", " ").replace(".", " ")

    index = book_name.find(" ") + 1

    book_name = book_name[index:]
    print(f'book name: {book_name}, url: {bookName_search_url}')
    return bookName_search_url, book_name


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
        gaussian = cv.GaussianBlur(self.__image, (3, 3), 1)
        gray = cv.cvtColor(gaussian, cv.COLOR_BGR2GRAY)
        edges = cv.Canny(gray, 50, 150, apertureSize=3)
        #
        # contours = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        # contours = contours[0] if len(contours) == 2 else contours[1]
        # big_contour = max(contours, key=cv.contourArea)

        rotated = cv.rotate(gray, cv.ROTATE_90_COUNTERCLOCKWISE)
        # cv.imshow(f'image', cv.rotate(self.__image, cv.ROTATE_90_COUNTERCLOCKWISE))
        config = "--psm 3"
        self.__book_info.ocr_output = pytesseract.image_to_string(rotated, config=config).strip()
        # print(f'ocr output:\n{self.__book_info.ocr_output}\ndone')
        # cv.waitKey(0)
        # for i in range(3):
        #     rotated = cv.rotate(gray, i)
        #     cv.imshow(f'rotated: {i}', rotated)
        #     cv.waitKey(0)
        #     ocr = pytesseract.image_to_string(rotated, config=config).strip()
        #     print(f'ocr output:\n{ocr}\ndone')
        #     if len(ocr) > len(self.__book_info.ocr_output):
        #         self.__book_info.ocr_output = ocr

    def __goodreads_search(self):
        """
        search book name by the ocr output
        """
        if len(self.__book_info.ocr_output) > 5:
            print(f'searching ({len(self.__book_info.ocr_output)}): {self.__book_info.ocr_output}')
            self.__book_info.book_url, self.__book_info.name = bookname_search(self.__book_info.ocr_output)

    def extract_book_info(self):
        self.__ocr()
        self.__goodreads_search()
        return self.__book_info

    def get_book_info(self):
        return self.__book_info


if __name__ == '__main__':
    # path = "images/output/2_9.png"
    # img = cv.imread(path)
    # # img = cv.resize(img, (322, 478))
    # # length = img.shape[0] if img.shape[0] > img.shape[1] else img.shape[1]
    # # scale = 500 / length
    # # print(f'scale: {scale}')
    # # if scale < 1:
    # #     img = cv.resize(img, (0, 0), fx=scale, fy=scale)
    # img = cv.rotate(img, cv.ROTATE_90_COUNTERCLOCKWISE)
    # cv.imshow("original", img)
    # gaussian = cv.GaussianBlur(img, (3, 3), 1)
    # gaussian2 = cv.GaussianBlur(img, (3, 3), 2)
    # cv.imshow('gu', gaussian)
    #
    # gray = cv.cvtColor(gaussian, cv.COLOR_BGR2GRAY)
    # gray2 = cv.cvtColor(gaussian2, cv.COLOR_BGR2GRAY)
    # cv.imshow('gb', gray)
    #
    # edges = cv.Canny(gray2, 50, 150, apertureSize=3)
    # cv.imshow('edges', edges)

    # gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # # adaptive_threshold = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 85, 11)
    # # adaptive_threshold = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    # # cv.imshow("adaptive_threshold", adaptive_threshold)
    # config = "--psm 3"
    # text = pytesseract.image_to_string(gray, config=config)
    # text2 = pytesseract.image_to_string(edges, config=config)
    #
    # print(text, "\n ------------------ \n", text2)

    # path = "images/output/0_{}.png"
    #
    # for i in range(15):
    #
    #     img = cv.imread(path.format(i))
    #     info_extractor = InfoExtractor(img)
    #     info_extractor.extract_book_info()
    #     info = info_extractor.get_book_info()
    #     print(f'book: {info}')
    #     cv.waitKey(0)

    path = "images/output/spines/8.jpg"
    img = cv.imread(path)
    gaussian = cv.GaussianBlur(img, (3, 3), 1)
    gray = cv.cvtColor(gaussian, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray, 50, 150, apertureSize=3)

    contours = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    print(contours)
    # big_contour = max(contours, key=cv.contourArea)
    # print(big_contour)
    # result = np.zeros_like(img)
    #
    # cv.drawContours(result, [big_contour], 0, (255, 255, 255), cv.FILLED)

    print(len(contours))

    result = np.zeros_like(img)
    cv.drawContours(result, contours, 0, (255, 255, 255), cv.FILLED)

    # save results
    # cv.imwrite('knife_edge_result.jpg', result)

    cv.imshow('result', result)
    cv.imshow('edges', edges)
    cv.waitKey(0)

    # print(info.name, "\n", info.ocr_output, "\n", info)
