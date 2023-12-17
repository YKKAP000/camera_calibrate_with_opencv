"""
EstimatePoseMarker.py

generate_board = CharucoBoard(dictionary type)

dictionary type
    dictionary = {
        "4X4_50": aruco.DICT_4X4_50,
        "5X5_50": aruco.DICT_5X5_50,
        "6X6_50": aruco.DICT_6X6_50,
        "7X7_50": aruco.DICT_7X7_50,
    }
"""
import os

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import sys
import numpy as np

import cv2
from CharucoBoard import CharucoBoard
from ArucoMarker import ArucoMarker
from util import load_config


def estimate_pose_single_markers(corners, marker_size, mtx, dist):
    """
        This will estimate the rvec and tvec for each of the marker corners detected by:
           corners, ids, rejectedImgPoints = detector.detectMarkers(image)
        corners - is an array of detected corners for each detected marker in the image
        marker_size - is the size of the detected markers
        mtx - is the camera matrix
        distortion - is the camera distortion matrix
        RETURN list of rvecs, tvecs, and trash (so that it corresponds to the old estimatePoseSingleMarkers())
    """
    marker_points = np.array([[-marker_size / 2, marker_size / 2, 0],
                              [marker_size / 2, marker_size / 2, 0],
                              [marker_size / 2, -marker_size / 2, 0],
                              [-marker_size / 2, -marker_size / 2, 0]], dtype=np.float32)
    trash = []
    rvecs = []
    tvecs = []

    for corner in corners:
        nada, rvec, tvec = cv2.solvePnP(marker_points, corner, mtx, dist, False, cv2.SOLVEPNP_IPPE_SQUARE)
        rvecs.append(rvec)
        tvecs.append(tvec)
        trash.append(nada)
    return rvecs, tvecs, trash


def main():
    # Create Charucoboard object
    marker = ArucoMarker("4X4_50")

    mtx, dist = load_config()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        # frame の 歪補正化 -> dist
        h, w = frame.shape[:2]
        new_cameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        dst = cv2.undistort(frame, mtx, dist, None, new_cameramtx)
        # crop the image
        x, y, w, h = roi
        dst = dst[y:y + h, x:x + w]

        cv2.imshow("raw", frame)
        # cv2.imshow('undistort', dst)

        marker_corners, marker_ids, _ = marker.detector.detectMarkers(dst)
        if not (marker_ids is None):
            rvecs, tvecs, _ = estimate_pose_single_markers(marker_corners, 5.3, new_cameramtx, dist)
            for idx in range(len(marker_ids)):
                cv2.drawFrameAxes(dst, mtx, dist, rvecs[idx], tvecs[idx], 5)
                print('marker id:%d, pos_x = %f,pos_y = %f, pos_z = %f' % (marker_ids[idx], tvecs[idx][0], tvecs[idx][1], tvecs[idx][2]))

        detect_frame = marker.draw_detected_markers(dst)
        # cv2.aruco.drawDetectedMarkers(dst, marker_corners, marker_ids)
        cv2.imshow("detect", detect_frame)

        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
