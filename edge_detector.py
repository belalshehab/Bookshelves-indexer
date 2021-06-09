import cv2 as cv
import numpy as np

from enum import Enum


#### constants ####
ANGLE = 0.96
LINE_PERC = 0.05
NEIGHBOURS_LIMIT = 15

class Orientation(Enum):
    UNKNOWN = 0
    VERTICAL = 1
    HORIZONTAL = 2


class Line:
    def __init__(self, *args):
        self.x1, self.y1, self.x2, self.y2 = args

        self.angle = 0
        self.length = 0
        self.orientation = Orientation.UNKNOWN
        self.center = 0
        self.strength = 0
        self.calculate_features()

    def calculate_features(self):
        height = self.y2 - self.y1
        width = self.x2 - self.x1

        if width != 0:
            self.angle = np.arctan(height / width)
        else:
            self.angle = np.pi / 2

        sine = abs(np.sin(self.angle))
        cos = abs(np.cos(self.angle))

        if sine > ANGLE:
            self.orientation = Orientation.VERTICAL
            self.length = height
            self.center = (self.x1 + self.x2) / 2
            self.strength = sine * height
        elif cos > ANGLE:
            self.orientation = Orientation.HORIZONTAL
            self.length = width
            self.center = (self.y1 + self.y2) / 2
            self.strength = cos * width


class ImageSegmentor:
    def __init__(self, image, orientation, debug=True):
        self.__orientation = orientation
        self.__debug = debug
        self.__original_image = image
        self.__image_width = self.__original_image.shape[1]
        self.__image_height = self.__original_image.shape[0]
        self.__image_length = self.__image_width if self.__orientation == Orientation.HORIZONTAL else self.__image_height
        self.__image_length_other = self.__image_height if self.__orientation == Orientation.HORIZONTAL else self.__image_width
        self.__image = None
        self.__all_lines = []
        self.__oriented_lines = []
        self.filtered_lines_by_center = []

        self.__segments = []

    def __draw_lines(self, lines, name='lines', shape=None, wait_key=False):
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

    def __fix_image(self):
        """
        preprocess image to:
            1. fix lightening issues
            2. convert image to gray scale
            3. apply gaussian filter
        """
        self.__image = cv.cvtColor(self.__original_image, cv.COLOR_BGR2GRAY)
        # self.__image = cv.blur(self.__image, (3, 3))
        # cv.imshow('fixed image', self.__image)

    def __extract_lines(self):
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
                if line.orientation == self.__orientation and line.length >= LINE_PERC * self.__image_length:
                    self.__oriented_lines.append(line)
        self.__oriented_lines.sort(key=lambda line: line.center)
        self.__draw_lines(self.__all_lines, 'All lines')
        self.__draw_lines(self.__oriented_lines, f'{self.__orientation.name.lower()} oriented lines')

    def __calculate_cuts_coordinates(self):
        for index in range(len(self.__oriented_lines)):
            i = 0
            self.__oriented_lines[index].strength += self.__oriented_lines[index].strength
            while index + i < len(self.__oriented_lines) and self.__oriented_lines[index + i].center - \
                    self.__oriented_lines[index].center <= NEIGHBOURS_LIMIT:
                self.__oriented_lines[index].strength += self.__oriented_lines[index + i].strength
                self.__oriented_lines[index + i].strength += self.__oriented_lines[index].strength
                i += 1

        self.filtered_lines_by_center = []
        if not self.__oriented_lines:
            return
        last_center = self.__oriented_lines[0].center
        max_line = self.__oriented_lines[0]
        for line in self.__oriented_lines:
            if line.strength < self.__image_width * 1.5 or line.length < 0.07 * self.__image_width:
                continue
            elif line.center - last_center < 10:
                if line.strength > max_line.strength:
                    max_line = line
                # max_line = line if line.strength > max_line.strength else max_line
            else:
                # x1, y1, x2, y2, avg_x, sine, strength = max_line
                self.filtered_lines_by_center.append(max_line)
                # cv2.line(mask2, (x1, y1), (x2, y2), (255, 0, 0), 1)
                # cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), 1)
                max_line = line
            last_center = line.center

        self.filtered_lines_by_center.append(max_line)

        self.__draw_lines(self.filtered_lines_by_center, f'filtered {self.__orientation.name.lower()} lines')

    def __extract_segments(self):
        if not self.filtered_lines_by_center:
            return 
        last_line = self.filtered_lines_by_center[0]
        cuts = [0]
        current_cut = 0
        num_lines = 0
        for line in self.filtered_lines_by_center:
            if line.center - last_line.center < self.__image_length_other / 30:
                current_cut += line.center
                num_lines += 1
            else:
                cuts.append(int(current_cut / max(num_lines, 1)))
                num_lines = 1
                current_cut = line.center
            last_line = line
        cuts.append(int(current_cut / max(num_lines, 1)))
        cuts.append(self.__image_length_other - 1)  # todo add this to filtered lines

        for cut_index in range(1, len(cuts)):
            if self.__orientation == Orientation.HORIZONTAL:
                segment = self.__original_image[cuts[cut_index - 1]: cuts[cut_index], 0: self.__image_length - 1]
            else:
                segment = self.__original_image[0: self.__image_length - 1, cuts[cut_index - 1]: cuts[cut_index]]
            self.__segments.append(segment)

            if self.__debug:
                cv.imshow(f'segment{cut_index}', segment)
                # cv.waitKey(0)

    def extract_segments(self):
        self.__fix_image()
        self.__extract_lines()
        self.__calculate_cuts_coordinates()
        self.__extract_segments()
        if self.__debug:
            cv.waitKey(0)

    def get_segments(self):
        return self.__segments


if __name__ == '__main__':
    path = 'images/02.png'
    image = cv.imread(path)

    shelves_segmentor = ImageSegmentor(image, Orientation.HORIZONTAL, debug=True)
    shelves_segmentor.extract_segments()

    shelves = shelves_segmentor.get_segments()

    print(f'shelves number: {len(shelves)}')
    for i, shelf in enumerate(shelves):
        cv.imwrite(f'images/output/shelf_{i}.png', shelf)
        spines_segmentor = ImageSegmentor(shelf, Orientation.VERTICAL, debug=True)
        spines_segmentor.extract_segments()
        spines = spines_segmentor.get_segments()

        for j, spine in enumerate(spines):
            cv.imwrite(f'images/output/spine_{i}.{j}.png', spine)

