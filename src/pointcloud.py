import numpy as np

def depth_to_pointcloud(depth_map):
    if depth_map is None:
        raise ValueError("Depth map이 없습니다.")

    h, w = depth_map.shape

    X, Y = np.meshgrid(np.arange(w), np.arange(h))
    Z = depth_map

    points = np.dstack((X, Y, Z))
    points = points.reshape(-1, 3)

    return points


