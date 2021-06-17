import copy

import cv2 as cv
import numpy as np

from skimage import measure
import imutils
from enum import Enum

Angle_Margin = 0.98


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
        height = abs(self.y2 - self.y1)
        width = abs(self.x2 - self.x1)

        if width != 0:
            self.angle = np.arctan(height / width)
        else:
            self.angle = np.pi / 2

        sine = abs(np.sin(self.angle))
        cos = abs(np.cos(self.angle))

        if sine > Angle_Margin:
            self.orientation = Orientation.VERTICAL
            self.length = height
            self.center = (self.x1 + self.x2) / 2
            self.strength = sine * height
        elif cos > Angle_Margin:
            self.orientation = Orientation.HORIZONTAL
            self.length = width
            self.center = (self.y1 + self.y2) / 2
            self.strength = cos * width


class ImageSegmenter:
    def __init__(self, image, orientation, config, debug=True):
        self.__original_image = image
        self.__orientation = orientation
        self.__config = config
        self.__debug = debug
        self.__image_width = self.__original_image.shape[1]
        self.__image_height = self.__original_image.shape[0]
        self.__image_length = self.__image_width if self.__orientation == Orientation.HORIZONTAL else self.__image_height
        self.__image_length_other = self.__image_height if self.__orientation == Orientation.HORIZONTAL else self.__image_width
        self.__image = None
        self.__all_lines = []
        self.__oriented_lines = []
        self.__filtered_lines_by_center = []
        self.__segments = []
        self.__segments_with_coordinates = []

    def __draw_lines(self, lines, name='lines', mask=None, print_strength=False):
        if self.__debug:
            if mask is None:
                mask = np.zeros_like(self.__image)
            for i, line in enumerate(lines):
                cv.line(mask, (line.x1, line.y1), (line.x2, line.y2), (255, 255, 0), 1)
                if print_strength:
                    cv.putText(mask, f'{i}:{round(line.strength)}', (line.x1, line.y1 - 1), cv.FONT_HERSHEY_SIMPLEX,
                               0.35, 255)

            cv.imshow(name, mask)

    def __fix_image(self):
        """
        preprocess image to:
            1. fix lightening issues
            2. convert image to gray scale
            3. apply gaussian filter
        """
        self.__image = cv.cvtColor(self.__original_image, cv.COLOR_BGR2GRAY)
        self.__image = cv.blur(self.__image, (3, 3))
        # cv.imshow('fixed image', self.__image)

    def __extract_lines(self):
        """
        extract lines from the image using Hough line detector, and calculate it's x and y center and
        the angle on horizontal access, then use only the oriented lines
        """
        edges = cv.Canny(self.__image, 50, 150, apertureSize=3)
        if self.__debug:
            cv.imshow('edges', edges)

        lines = cv.HoughLinesP(edges, 1, np.pi / 180, 150, maxLineGap=5).squeeze()
        for x1, y1, x2, y2 in lines:
            line = Line(x1, y1, x2, y2)
            self.__all_lines.append(line)
            if line.orientation == self.__orientation and line.length >= 0.06 * self.__image_length:
                self.__oriented_lines.append(line)
        self.__oriented_lines.sort(key=lambda line: line.center)
        self.__draw_lines(self.__all_lines, 'All lines')
        self.__draw_lines(self.__oriented_lines, f'{self.__orientation.name.lower()} oriented lines',
                          print_strength=True)

    def __remove_close_to_boundaries_lines(self):
        """
        removes lines that is very close to image boundries
        """
        lower_boundary = self.__config['boundaries_offset'] * self.__image_length_other
        upper_boundary = (1 - self.__config['boundaries_offset']) * self.__image_length_other
        self.__oriented_lines = [line for line in self.__oriented_lines if
                                 lower_boundary < line.center < upper_boundary]

    def __vote_for_strong_lines(self):
        """
        1. vote for lines with high strength and close neighbours.
        2. remove the lines with very small length or less than minimum strength
        """
        strengthened = copy.deepcopy(self.__oriented_lines)
        neighbours_distance = self.__config.get('neighbours_distance', 0.1) * self.__image_length_other
        for index, line in enumerate(self.__oriented_lines):
            i = 1
            strengthened[index].strength += 7 * line.strength
            while index + i < len(self.__oriented_lines) and \
                    self.__oriented_lines[index + i].center - self.__oriented_lines[
                index].center <= neighbours_distance:
                strengthened[index].strength += self.__oriented_lines[index + i].strength
                strengthened[index + i].strength += line.strength
                i += 1

        minimum_strength = self.__config.get('minimum_strength', 0.85) * self.__image_length
        minimum_length = self.__config.get('minimum_length', 0.03) * self.__image_length
        self.__oriented_lines = [line for line in strengthened if
                                 line.strength > minimum_strength and line.length > minimum_length]

    def __remove_duplicate_lines(self):
        """
        remove duplicate lines by choosing the strongest line
        """
        self.__draw_lines(self.__oriented_lines, f'{self.__orientation.name.lower()} lines strengthened',
                          print_strength=True)
        self.__filtered_lines_by_center.clear()
        if not self.__oriented_lines:
            return
        neighbours_distance = self.__config.get('neighbours_distance', 0.1) * self.__image_length_other
        last_center = self.__oriented_lines[0].center
        max_line = self.__oriented_lines[0]
        for index, line in enumerate(self.__oriented_lines):
            if line.center - last_center < neighbours_distance:
                if line.strength > max_line.strength:
                    max_line = line
            else:
                self.__filtered_lines_by_center.append(max_line)
                max_line = line
            last_center = line.center
        self.__filtered_lines_by_center.append(max_line)

        self.__draw_lines(self.__filtered_lines_by_center, f'filtered {self.__orientation.name.lower()} lines',
                          print_strength=True)
        self.__draw_lines(self.__filtered_lines_by_center, f'filtered {self.__orientation.name.lower()} lines image',
                          mask=self.__image)

    def __extract_segments(self):
        """
        prepare the cutoffs and segment the image
        """
        if not self.__filtered_lines_by_center:
            return
        cuts = []
        current_cut = 0
        for line in self.__filtered_lines_by_center:
            cuts.append(current_cut)
            current_cut = int(line.center)
        cuts.append(current_cut)
        cuts.append(self.__image_length_other - 1)

        self.__segments.clear()
        self.__segments_with_coordinates.clear()

        for cut_index in range(1, len(cuts)):
            lower_point = cuts[cut_index - 1]
            upper_point = cuts[cut_index]
            if self.__orientation == Orientation.HORIZONTAL:
                segment = self.__original_image[lower_point: upper_point, : ]
            else:
                segment = self.__original_image[ : , lower_point: upper_point]
            self.__segments.append(segment)
            self.__segments_with_coordinates.append((segment, lower_point, upper_point))

    def extract_segments(self):
        self.__fix_image()
        self.__extract_lines()
        self.__remove_close_to_boundaries_lines()
        self.__vote_for_strong_lines()
        self.__remove_duplicate_lines()
        self.__extract_segments()
        if self.__debug:
            cv.waitKey(0)

    def get_segments(self):
        return self.__segments

    def get_segments_with_coordinates(self):
        return self.__segments_with_coordinates

def fix_glare(image):
    # resize the image
    # image = imutils.resize(image, height=500)
    masked_image = np.copy(image)

    # #take copy of image
    # orig = image.copy()

    # convert image to gray scale
    # gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    ########### to know glared areas
    # convert to binary
    thresh = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)[1]

    # remove noises
    thresh = cv.erode(thresh, None, iterations=2)
    thresh = cv.dilate(thresh, None, iterations=4)

    labels = measure.label(thresh, connectivity=2, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")

    # loop over the unique components
    for label in np.unique(labels):
        # if this is the background label, ignore it
        if label == 0:
            continue

        # otherwise, construct the label mask and count the
        # number of pixels
        labelMask = np.zeros(thresh.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv.countNonZero(labelMask)
        masked_image[mask != 0] = [0, 0, 0]

        # if the number of pixels in the component is sufficiently
        # large, then add it to our mask of "large blobs"
        if numPixels > 300:
            mask = cv.add(mask, labelMask)

    # find the contours in the mask, then sort them from left to right
    cnts = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # edit light of contour
    brightness = 50
    contrast = 30

    cnt_image = image - masked_image
    cnt_image = np.int16(cnt_image)
    cnt_image = cnt_image * (contrast / 127 + 1) - contrast - brightness
    cnt_image = np.clip(cnt_image, 0, 255)
    cnt_image = np.uint8(cnt_image)

    unglared_image = masked_image + cnt_image
    return unglared_image


def get_shelves(image):
    config = {
        'minimum_length': 0.03,
        'minimum_strength': 0.85,
        'boundaries_offset': 0.1,
        'neighbours_distance': 0.1
    }

    shelves_segmenter = ImageSegmenter(image, Orientation.HORIZONTAL, config, debug=False)
    shelves_segmenter.extract_segments()
    shelves = shelves_segmenter.get_segments()

    return shelves


def get_spines(shelf):
    config = {
        'minimum_length': 0.03,
        'minimum_strength': 0.85,
        'boundaries_offset': 0.001,
        'neighbours_distance': 0.1
    }

    spines_segmenter = ImageSegmenter(shelf, Orientation.VERTICAL, config, debug=True)
    spines_segmenter.extract_segments()
    spines = spines_segmenter.get_segments()
    print(f'spines number: {len(spines)}')
    for j, spine in enumerate(spines):
        cv.imshow(f'{i}:{j}', spine)
    cv.waitKey(0)

    return spines


if __name__ == '__main__':
    path = 'images/maktaba/0{}.jpg'
    # config = {
    #     'minimum_length': 0.03,
    #     'minimum_strength': 0.85,
    #     'boundaries_offset': 0.1,
    #     'neighbours_distance': 0.1
    # }

    for i in range(1, 10):
        image = cv.imread(path.format(i))
        cv.imshow(f'{i}', image)
        shelves = get_shelves(image)
        print(f'shelves number: {len(shelves)}')
        for j, shelf in enumerate(shelves):
            cv.imwrite(f'images/output/{i}_{j}.jpg', shelf)
            cv.imshow(f'{i}:{j}', shelf)
        cv.waitKey(0)

    # path = 'images/maktaba/01.jpg'
    # image = cv.imread(path)
    # shelves = get_shelves(image)
    #
    # get_spines(shelves[0])
    # #
    # # for i, shelf in enumerate(shelves):
    # #     if shelf.shape[0] < 0.2 * image.shape[0]:
    # #         continue
    # #     cv.imwrite(f'images/output/shelf_{i}.png', shelf)
    # #     spines_segmenter = ImageSegmenter(shelf, Orientation.VERTICAL, config, debug=True)
    # #     spines_segmenter.extract_segments()
    # #     spines = spines_segmenter.get_segments()
    # #
    # #     for j, spine in enumerate(spines):
    # #         cv.imwrite(f'images/output/spine_{i}.{j}.png', spine)
    #
    # cv.waitKey(0)
