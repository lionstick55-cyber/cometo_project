import os
import sys
import argparse
import cv2
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(
        description="YOLOv8 inference + OpenCV visualization (per-class thresholds)"
    )
    parser.add_argument(
        "image",
        help="이미지 파일명 또는 경로 (예: test.jpg 또는 C:\\path\\test.jpg)"
    )
    parser.add_argument(
        "--model",
        default="best.pt",
        help="모델 파일명/경로 (기본: week3/best.pt)"
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="추론 이미지 사이즈 (예: 640, 960)"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.03,
        help="YOLO predict 단계 conf (후보를 넓게 가져오려면 낮게)"
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.55,
        help="NMS IoU (낮추면 덜 합쳐져서 박스 수 늘 수 있음)"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="창으로 결과를 띄움 (서버/코랩 환경이면 끄는 게 좋음)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="결과 이미지를 저장함 (기본 True로 쓰고 싶으면 아래에서 True로 바꿔도 됨)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    week3_dir = os.path.dirname(os.path.abspath(__file__))

    # ✅ 모델 경로 처리 (상대경로면 week3 기준)
    model_path = args.model
    if not os.path.isabs(model_path):
        model_path = os.path.join(week3_dir, model_path)

    if not os.path.exists(model_path):
        print("❌ 모델 파일을 찾을 수 없습니다:", model_path)
        print("   예) week3 폴더에 best.pt 또는 best_y8n_e15.pt가 있는지 확인")
        return

    # ✅ 이미지 경로 처리 (상대경로면 week3 기준)
    input_path = args.image
    if not os.path.isabs(input_path):
        input_path = os.path.join(week3_dir, input_path)

    if not os.path.exists(input_path):
        print("❌ 이미지 파일을 찾을 수 없습니다:", input_path)
        return

    image = cv2.imread(input_path)
    if image is None:
        print("❌ 이미지 로드 실패:", input_path)
        return

    model = YOLO(model_path)
    print("✅ 모델 로드:", model_path)
    print("✅ 모델 클래스:", model.names)

    # ✅ 예측은 넓게(conf 낮게), 표시(그리기)는 클래스별 임계값으로 제어
    results = model.predict(
        source=image,
        conf=args.conf,
        iou=args.iou,
        imgsz=args.imgsz,
        verbose=False
    )

    # ✅ 클래스별 표시 임계값 (여기만 조절하면 됨)
    show_thr = {
        "person": 0.25,
        "dog": 0.05,
        "car": 0.20,
    }

    # ✅ 클래스별 색상(BGR)
    colors = {
        "person": (0, 0, 255),      # 빨강
        "dog": (255, 0, 0),         # 파랑
        "car": (0, 255, 255),       # 노랑
    }

    drawn = {"person": 0, "dog": 0, "car": 0, "other": 0}

    # 결과가 여러 장일 수도 있어(보통 1장)
    for r in results:
        names = r.names  # id -> label
        if r.boxes is None:
            continue

        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            label = names[cls_id]  # 'person', 'dog', 'car' (또는 기타)
            thr = show_thr.get(label, 0.25)
            if conf < thr:
                continue

            color = colors.get(label, (0, 255, 0))

            # 박스
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 1)

            # 텍스트(배경 포함)
            text = f"{label} {conf:.2f}"
            (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            y0 = max(0, y1 - h - 4)
            cv2.rectangle(image, (x1, y0), (x1 + w + 2, y1), color, -1)
            cv2.putText(
                image,
                text,
                (x1 + 1, y1 - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                1
            )

            if label in drawn:
                drawn[label] += 1
            else:
                drawn["other"] += 1

    # ✅ 저장
    out_path = None
    if args.save or True:  # 항상 저장하고 싶으면 True 유지
        out_dir = os.path.join(week3_dir, "results")
        os.makedirs(out_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        out_path = os.path.join(out_dir, f"result_{base_name}.jpg")
        cv2.imwrite(out_path, image)

    print("💾 저장 완료:", out_path if out_path else "(저장 안 함)")
    print("📌 표시된 박스 개수:", drawn)
    print(f"⚙️  predict conf={args.conf}, iou={args.iou}, imgsz={args.imgsz}")
    print(f"🎛️  show_thr={show_thr}")

    # ✅ 화면 표시
    if args.show:
        cv2.imshow("YOLO Detection Result", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()