import cv2 as cv
import numpy as np


class Line:
    def __init__(self, *args):
        self.x1, self.y1, self.x2, self.y2 = args

        self.x_center = (self.x1 + self.x2) / 2
        self.y_center = (self.y1 + self.y2) / 2
        self.height = self.y2 - self.y1
        self.width = self.x2 - self.x1

        if self.width != 0:
            self.angle = np.arctan(self.height / self.width)
        else:
            self.angle = np.pi / 2

        self.length = np.sqrt(self.width ** 2 + self.height ** 2)
        self.horizontal = False
        self.vertical = False
        self.strength = 0
        self.calculate_orientation()

    def calculate_orientation(self):
        """
        update orientation and strength only if the line is horizontal or vertical
        """
        sine = abs(np.sin(self.angle))
        cos = abs(np.cos(self.angle))

        if sine > 0.96:
            self.horizontal = True
            self.strength = sine * self.width
        elif abs(np.cos(self.angle)) > 0.96:
            self.vertical = True
            self.strength = cos * self.height


class BoundaryExtraction:
    def __init__(self, image, debug=True):
        self.__debug = debug
        self.__original_image = image
        self.width = self.__original_image.shape[1]
        self.height = self.__original_image.shape[0]
        self.__image = None
        self.__all_lines = []
        self.__horizontal_strong_lines = []
        self.__vertical_strong_lines = []

    def draw_lines(self, lines, shape, name='lines', wait_key=False):
        if self.__debug:
            fld_lines = []
            mask = np.zeros(shape)

            fld = cv.ximgproc.createFastLineDetector()
            for line in lines:
                fld_lines.append([line.x1, line.y1, line.x2, line.y2])
            fld_lines = np.array(fld_lines)
            mask = fld.drawSegments(mask, fld_lines)
            cv.imshow(name, mask)
            if wait_key:
                cv.waitKey(0)

    def fix_image(self):
        """
        preprocess image to:
            1. fix lightening issues
            2. convert image to gray scale
            3. apply gaussian filter
        """
        self.__image = cv.cvtColor(self.__original_image, cv.COLOR_BGR2GRAY)

    def extract_lines(self):
        """
        extract lines from the image using opencv fast line detector, and calculate it's x and y center and
        the angle on horizontal access
        """
        fld = cv.ximgproc.createFastLineDetector()
        lines = fld.detect(self.__image)
        for lele in lines:
            for x1, y1, x2, y2 in lele:
                self.__all_lines.append(Line(x1, y1, x2, y2))

        self.draw_lines(self.__all_lines, self.__image.shape, 'All lines')

    def extract_shelves(self):
        max_line = self.__all_lines[0]
        last_y_center = max_line.y_center
        filtered_lines_by_y_center = []
        for i, line in enumerate(self.__all_lines):
            if not line.horizontal:
                continue
            if not (line.horizontal and line.width >= (self.width * 0.25)):
                continue
            if (line.y_center - last_y_center) < 10:
                if line.strength > max_line.strength:
                    max_line = line
            else:
                filtered_lines_by_y_center.append(max_line)
                max_line = line
            last_y_center = line.y_center
        filtered_lines_by_y_center.append(max_line)

        self.draw_lines(filtered_lines_by_y_center, self.__image.shape, 'horizontal lines')


    def extract_spines(self):
        pass

    def extract_books(self):
        self.fix_image()
        self.extract_lines()
        self.extract_shelves()
        if self.__debug:
            cv.waitKey(0)


if __name__ == '__main__':
    path = 'images/01.png'
    image = cv.imread(path)

    be = BoundaryExtraction(image)
    be.extract_books()

    x = np.arctan(float('inf'))

    print(x)
