import cv2 as cv
from googlesearch import search
from book import Book
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def bookname_search(text):
    goodreads_url_prefix = "https://www.goodreads.com/book/show/"
    gen = search(text + " " + goodreads_url_prefix, tld='com', lang='en', num=1, pause=5)
    bookName_search_url = next(gen)
    bookName = bookName_search_url[bookName_search_url.rfind(".") + 1:]
    book_name = bookName.replace("_", " ")
    # print(bookName_search_url, "\n", bookName, "\n", book_name)

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
        # self.__image = cv.rotate(self.__image, cv.ROTATE_90_COUNTERCLOCKWISE)
        gray = cv.cvtColor(self.__image, cv.COLOR_BGR2GRAY)
        config = "--psm 3"
        self.__book_info.ocr_output = pytesseract.image_to_string(gray, config=config)

    def __goodreads_search(self):
        """
        search book name by the ocr output
        """
        self.__book_info.book_url, self.__book_info.name = bookname_search(self.__book_info.ocr_output)

    def extract_book_info(self):
        self.__ocr()
        self.__goodreads_search()

    def get_book_info(self):
        return self.__book_info


if __name__ == '__main__':
    path = 'D:/college/2nd semester/image processing/Prroject/Book-spine-extractor/SpineClassifier/images/spines/10.jpg'
    img = cv.imread(path)
    # img = cv.rotate(img, cv.ROTATE_90_COUNTERCLOCKWISE)
    cv.imshow("original", img)
    # gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # # adaptive_threshold = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 85, 11)
    # # adaptive_threshold = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    # # cv.imshow("adaptive_threshold", adaptive_threshold)
    # config = "--psm 3"
    # text = pytesseract.image_to_string(gray, config=config)
    # print(text)

    info_extractor = InfoExtractor(img)
    info_extractor.extract_book_info()
    info = info_extractor.get_book_info()

    print(info.name, "\n", info.ocr_output, "\n", info.book_url)
    cv.waitKey(0)