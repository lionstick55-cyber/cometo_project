import os
import cv2
import numpy as np
from datasets import load_dataset
from PIL import Image
import random

# ==============================
# 설정 값
# ==============================
OUTPUT_DIR = "preprocessed_samples"
IMG_SIZE = 224
DARK_THRESHOLD = 30          # 평균 밝기 기준
MIN_OBJECT_RATIO = 0.05      # 객체 최소 비율 (5%)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================
# 1️⃣ 데이터셋 로드
# ==============================
print("Loading dataset...")
dataset = load_dataset("ethz/food101", split="train[:50]")  # 일부만 사용 (속도 고려)

saved_count = 0


# ==============================
# 2️⃣ 전처리 함수
# ==============================
def preprocess_image(pil_image):

    # PIL → numpy
    image = np.array(pil_image)

    # Resize
    image = cv2.resize(image, (IMG_SIZE, IMG_SIZE))

    # Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # 평균 밝기 계산 (이상치 제거용)
    mean_brightness = np.mean(gray)
    if mean_brightness < DARK_THRESHOLD:
        return None

    # Blur 적용
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 객체 크기 비율 계산 (threshold 기반)
    _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)
    object_ratio = np.sum(thresh == 255) / (IMG_SIZE * IMG_SIZE)

    if object_ratio < MIN_OBJECT_RATIO:
        return None

    # Normalize (0~1)
    normalized = blurred / 255.0

    return normalized


# ==============================
# 3️⃣ 데이터 증강 함수
# ==============================
def augment_image(image):

    augmented_images = []

    # 좌우 반전
    flipped = cv2.flip(image, 1)
    augmented_images.append(flipped)

    # 회전
    angle = random.choice([15, -15, 30, -30])
    M = cv2.getRotationMatrix2D((IMG_SIZE // 2, IMG_SIZE // 2), angle, 1)
    rotated = cv2.warpAffine(image, M, (IMG_SIZE, IMG_SIZE))
    augmented_images.append(rotated)

    # 밝기 변화
    brightness_factor = random.uniform(0.7, 1.3)
    bright = np.clip(image * brightness_factor, 0, 1)
    augmented_images.append(bright)

    return augmented_images


# ==============================
# 4️⃣ 전체 처리
# ==============================
for idx, data in enumerate(dataset):

    if saved_count >= 5:
        break

    pil_image = data["image"]

    processed = preprocess_image(pil_image)

    if processed is None:
        continue

    # 저장 (원본 전처리)
    save_path = os.path.join(OUTPUT_DIR, f"image_{saved_count}_original.jpg")
    cv2.imwrite(save_path, (processed * 255).astype(np.uint8))

    # 데이터 증강 후 저장
    augmented_list = augment_image(processed)

    for i, aug_img in enumerate(augmented_list):
        if saved_count >= 5:
            break

        save_path = os.path.join(OUTPUT_DIR, f"image_{saved_count}_aug{i}.jpg")
        cv2.imwrite(save_path, (aug_img * 255).astype(np.uint8))
        saved_count += 1

print("Preprocessing completed!")
