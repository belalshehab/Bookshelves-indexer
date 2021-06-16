from imutils import paths
import numpy as np
import argparse
import imutils

import cv2

path = 'images/q{}.jpg'
# im =
# cv2.imshow('x', im)
# cv2.waitKey(0)
images = [
    cv2.imread(path.format('1')),
    cv2.imread(path.format('2')),
    cv2.imread(path.format('3'))
]

# cv2.imshow("image 1", images[0])
# cv2.imshow("image 2", images[1])
# cv2.imshow("image 3", images[2])
# cv2.waitKey(0)

stitcher = cv2.Stitcher_create()

(status, stitched) = stitcher.stitch(images)

# if the status is '0', then OpenCV successfully performed image
# stitching
if status == 0:
    # write the output stitched image to disk
    cv2.imwrite('images/panorama.jpg', stitched)
    # display the output stitched image to our screen
    cv2.imshow("Stitched", stitched)
    cv2.waitKey(0)
# otherwise the stitching failed, likely due to not enough keypoints)
# being detected
else:
    print("[INFO] image stitching failed ({})".format(status))
