
import cv2
import numpy as np

def align_form(input_img, ref_img):
    # Convert both to grayscale
    gray_ref = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
    gray_input = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)

    # Detect ORB keypoints and descriptors
    orb = cv2.ORB_create(5000)
    kp1, des1 = orb.detectAndCompute(gray_ref, None)
    kp2, des2 = orb.detectAndCompute(gray_input, None)

    # Match features
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(matcher.match(des1, des2), key=lambda x: x.distance)

    # Take top 50 matches
    matches = matches[:50]

    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Compute Homography
    M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
    h, w = ref_img.shape[:2]
    aligned = cv2.warpPerspective(input_img, M, (w, h))

    return aligned
