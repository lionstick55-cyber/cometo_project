import numpy as np
import cv2

def create_depth_map(image):

    if image is None:
        raise ValueError("입력 이미지가 없습니다.")

    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    depth = image.astype(np.float32) / 255.0

    return depth
