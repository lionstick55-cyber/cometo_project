# src/depth_dpt.py

import os
import torch
import numpy as np
from PIL import Image
import cv2
from transformers import DPTImageProcessor, DPTForDepthEstimation


def run_dpt(image_name: str) -> None:
    """
    depth_bf_af_images 폴더에 있는 원본 이미지를 입력받아
    같은 폴더에 DPT 결과를 저장합니다.

    저장 파일:
      - dpt_depth_<원본이름>.png
      - dpt_depth_color_<원본이름>.png
    """

    # ✅ 실행 위치에 상관없이 프로젝트 루트 기준으로 경로를 잡기
    # 현재 파일: .../src/depth_dpt.py
    # 프로젝트 루트: .../ (src의 상위 폴더)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_folder = os.path.join(BASE_DIR, "depth_bf_af_images")

    # 입력 이미지 경로
    image_path = os.path.join(base_folder, image_name)

    if not os.path.exists(image_path):
        print("이미지 파일이 존재하지 않습니다:", image_path)
        return

    # 이미지 로드 (PIL)
    image = Image.open(image_path).convert("RGB")

    # 모델 로드 (최초 1회 다운로드될 수 있음)
    model_name = "Intel/dpt-large"
    image_processor = DPTImageProcessor.from_pretrained(model_name)
    model = DPTForDepthEstimation.from_pretrained(model_name)
    model.eval()

    # Depth 추론
    inputs = image_processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        predicted_depth = outputs.predicted_depth  # (1, H, W)

    # Depth 정규화 (0~255)
    depth = predicted_depth.squeeze().cpu().numpy()
    depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8)  # 0 나눔 방지
    depth_uint8 = (depth * 255).astype("uint8")

    # 컬러맵 적용
    depth_color = cv2.applyColorMap(depth_uint8, cv2.COLORMAP_JET)

    # 출력 파일명 구성
    name, _ = os.path.splitext(image_name)
    gray_path = os.path.join(base_folder, f"dpt_depth_{name}.png")
    color_path = os.path.join(base_folder, f"dpt_depth_color_{name}.png")

    # 저장
    cv2.imwrite(gray_path, depth_uint8)
    cv2.imwrite(color_path, depth_color)

    print("DPT 결과 저장 완료!")
    print(" -", os.path.abspath(gray_path))
    print(" -", os.path.abspath(color_path))


if __name__ == "__main__":
    image_name = input("depth_bf_af_images 폴더 안의 이미지 이름을 입력하세요: ")
    run_dpt(image_name)





