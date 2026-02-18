import os
import cv2
import numpy as np
import random
from datasets import load_dataset

# -------------------------------
# 1. 저장 폴더 생성
# -------------------------------
os.makedirs("preprocessed_samples", exist_ok=True)

# -------------------------------
# 2. 데이터셋 로드
# -------------------------------
dataset = load_dataset("ethz/food101", split="train")

# 완전 랜덤 셔플
dataset = dataset.shuffle(seed=random.randint(0, 10000))

# -------------------------------
# 3. 이상치 제거 함수
# -------------------------------

def is_too_dark(image, threshold=50):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.mean(gray) < threshold


def is_object_too_small(image, min_area_ratio=0.05):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
    white_pixels = np.sum(thresh == 255)
    total_pixels = image.shape[0] * image.shape[1]
    return (white_pixels / total_pixels) < min_area_ratio


# -------------------------------
# 4. 전처리 함수
# -------------------------------

def preprocess_image(image):
    # Resize
    image = cv2.resize(image, (224, 224))

    # 이상치 제거
    if is_too_dark(image):
        return None
    if is_object_too_small(image):
        return None

    # Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Normalize (0~1)
    normalized = gray / 255.0

    # Blur
    blurred = cv2.GaussianBlur(normalized, (5, 5), 0)

    # 다시 0~255 범위로 변환
    processed = (blurred * 255).astype(np.uint8)

    return processed


# -------------------------------
# 5. 랜덤 이미지 5장 저장
# -------------------------------

count = 0
index = 0

while count < 5 and index < len(dataset):
    image = np.array(dataset[index]["image"])

    processed = preprocess_image(image)

    if processed is not None:
        cv2.imwrite(f"preprocessed_samples/random_sample_{count+1}.jpg", processed)
        count += 1

    index += 1

print("✅ 랜덤 전처리 완료! 5장 저장되었습니다.")
