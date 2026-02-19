import numpy as np
import pytest
from src.depth_map import create_depth_map
from src.pointcloud import depth_to_pointcloud

def test_depth_map_shape():
    image = np.ones((100, 100), dtype=np.uint8) * 255
    depth = create_depth_map(image)
    assert depth.shape == image.shape

def test_depth_range():
    image = np.ones((100, 100), dtype=np.uint8) * 255
    depth = create_depth_map(image)
    assert depth.max() <= 1.0
    assert depth.min() >= 0.0

def test_pointcloud_shape():
    depth = np.ones((10, 10), dtype=np.float32)
    points = depth_to_pointcloud(depth)
    assert points.shape == (100, 3)

def test_none_input():
    with pytest.raises(ValueError):
        create_depth_map(None)
