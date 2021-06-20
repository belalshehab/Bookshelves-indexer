import cv2 as cv
from googlesearch import search
from book import Book
import pytesseract


# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def bookname_search(text):
    goodreads_url_prefix = "https://www.goodreads.com/book/show/"
    gen = search(text + " " + goodreads_url_prefix, tld='com', lang='en', num=1, pause=4)
    bookName_search_url = next(gen)
    bookName = bookName_search_url[bookName_search_url.find("-") + 1:]
    book_name = bookName.replace("-", " ")

    # bookName = bookName_search_url[bookName_search_url.rfind(".") + 1:]
    # book_name = bookName.replace("_", " ")

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

        rotated = cv.rotate(gray, cv.ROTATE_90_COUNTERCLOCKWISE)
        cv.imshow(f'gray', rotated)
        config = "--psm 3"
        self.__book_info.ocr_output = pytesseract.image_to_string(rotated, config=config).strip()
        print(f'ocr output:\n{self.__book_info.ocr_output}\ndone')
        cv.waitKey(0)
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
        # self.__goodreads_search()
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

    path = "images/output/0_{}.png"

    for i in range(15):

        img = cv.imread(path.format(i))
        info_extractor = InfoExtractor(img)
        info_extractor.extract_book_info()
        info = info_extractor.get_book_info()
        print(f'book: {info}')
        cv.waitKey(0)

    # print(info.name, "\n", info.ocr_output, "\n", info)
