import cv2
import os
import numpy as np

from src.depth_map import create_depth_map
from src.pointcloud import depth_to_pointcloud


def save_xyz(points: np.ndarray, path: str) -> None:
    """
    points: (N, 3) float array
    xyz 텍스트 형식으로 저장 (뷰어에서 열기 쉬움)
    """
    # 헤더 없이 x y z만 저장
    np.savetxt(path, points, fmt="%.6f")


def run_depth_and_3d(image_name: str) -> None:
    folder = "depth_bf_af_images"
    image_path = os.path.join(folder, image_name)

    if not os.path.exists(image_path):
        print("파일이 존재하지 않습니다:", image_path)
        return

    image = cv2.imread(image_path)
    if image is None:
        print("이미지를 불러올 수 없습니다.")
        return

    # Depth 생성 (0~1)
    depth_map = create_depth_map(image)

    # Depth 이미지(0~255)
    depth_uint8 = (depth_map * 255).astype("uint8")
    depth_color = cv2.applyColorMap(depth_uint8, cv2.COLORMAP_JET)

    name, _ = os.path.splitext(image_name)

    # ✅ depth 2장 저장
    gray_path = os.path.join(folder, f"depth_{name}.png")
    color_path = os.path.join(folder, f"depth_color_{name}.png")
    cv2.imwrite(gray_path, depth_uint8)
    cv2.imwrite(color_path, depth_color)

    # ✅ 3D Point Cloud 저장 (xyz)
    points = depth_to_pointcloud(depth_map)  # (H*W, 3)
    xyz_path = os.path.join(folder, f"pointcloud_{name}.xyz")
    save_xyz(points, xyz_path)

    print("저장 완료:")
    print(" -", gray_path)
    print(" -", color_path)
    print(" -", xyz_path)
    print("Point Cloud shape:", points.shape)


if __name__ == "__main__":
    image_name = input("depth_bf_af_images 폴더 안의 이미지 이름을 입력하세요: ")
    run_depth_and_3d(image_name)

