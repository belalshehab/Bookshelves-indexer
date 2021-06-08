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
            self.vertical = True
            self.strength = sine * self.height
        elif cos > 0.96:
            self.horizontal = True
            self.strength = cos * self.width


class BoundaryExtraction:
    def __init__(self, image, debug=True):
        self.__debug = debug
        self.__original_image = image
        self.width = self.__original_image.shape[1]
        self.height = self.__original_image.shape[0]
        self.__image = None
        self.__all_lines = []
        self.__horizontal_lines = []
        self.filtered_lines_by_y_center = []
        self.__vertical_lines = []

        self.__shelves = []

    def draw_lines(self, lines, name='lines', shape=None, wait_key=False):
        if self.__debug:
            fld_lines = []
            if not shape:
                shape = self.__image.shape
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
        # self.__image = cv.blur(self.__image, (3, 3))
        # cv.imshow('fixed image', self.__image)

    def extract_lines(self):
        """
        extract lines from the image using opencv fast line detector, and calculate it's x and y center and
        the angle on horizontal access
        """
        fld = cv.ximgproc.createFastLineDetector()
        fld_output = fld.detect(self.__image)
        for lines in fld_output:
            for x1, y1, x2, y2 in lines:
                line = Line(x1, y1, x2, y2)
                self.__all_lines.append(line)
                if line.horizontal and line.width >= 0.07 * self.width:
                    self.__horizontal_lines.append(line)
                elif line.vertical and line.height >= 0.07 * self.height:
                    self.__vertical_lines.append(line)

        self.draw_lines(self.__all_lines, 'All lines')
        self.draw_lines(self.__horizontal_lines, 'horizontal')
        self.draw_lines(self.__vertical_lines, 'vertical')

    def extract_shelves_coordinates(self):
        for index in range(len(self.__horizontal_lines)):
            i = 0
            self.__horizontal_lines[index].strength += self.__horizontal_lines[index].strength
            while index + i < len(self.__horizontal_lines) and self.__horizontal_lines[index + i].y_center - self.__horizontal_lines[index].y_center <= 15:
                self.__horizontal_lines[index].strength += self.__horizontal_lines[index + i].strength
                self.__horizontal_lines[index + i].strength += self.__horizontal_lines[index].strength
                i += 1

        self.filtered_lines_by_y_center = []
        last_y_center = self.__horizontal_lines[0].y_center
        max_line = self.__horizontal_lines[0]
        for line in self.__horizontal_lines:
            if line.strength < self.width * 1.5 or line.width < 0.07 * self.width:
                continue
            elif line.y_center - last_y_center < 10:
                if line.strength > max_line.strength:
                    max_line = line
                # max_line = line if line.strength > max_line.strength else max_line
            else:
                # x1, y1, x2, y2, avg_x, sine, strength = max_line
                self.filtered_lines_by_y_center.append(max_line)
                # cv2.line(mask2, (x1, y1), (x2, y2), (255, 0, 0), 1)
                # cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), 1)
                max_line = line
            last_y_center = line.y_center

        self.filtered_lines_by_y_center.append(max_line)

        self.draw_lines(self.filtered_lines_by_y_center, 'horizontal lines')

    def extract_shelves(self):
        last_line = self.filtered_lines_by_y_center[0]
        y_cuts = [0]
        current_y_cut = 0
        num_lines = 0
        for line in self.filtered_lines_by_y_center:
            if line.y_center - last_line.y_center < self.height / 30:
                current_y_cut += line.y_center
                num_lines += 1
            else:
                y_cuts.append(int(current_y_cut / max(num_lines, 1)))
                num_lines = 1
                current_y_cut = line.y_center
            last_line = line
        y_cuts.append(int(current_y_cut / max(num_lines, 1)))
        y_cuts.append(self.height - 1)  # todo add this to filtered lines

        print(f'y_cuts: {y_cuts}')
        # for cut in y_cuts:
        #     cv2.line(self.image, (cut, 0), (cut, self.image.shape[0] - 1), (0, 0, 255), 1)

        for cut_index in range(1, len(y_cuts)):
            shelf = self.__image[y_cuts[cut_index - 1]: y_cuts[cut_index], 0: self.width - 1]
            # spine = imutils.rotate(spine, 90)
            self.__shelves.append(shelf)

            cv.imshow(f'shelf{cut_index}', shelf)

        # cv.waitKey(0)

    def extract_spines(self):
        pass

    def extract_books(self):
        self.fix_image()
        self.extract_lines()
        self.extract_shelves_coordinates()
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
