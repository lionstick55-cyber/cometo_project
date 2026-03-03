from ultralytics import YOLO
import os

def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))   # week3
    project_root = os.path.dirname(this_dir)                # cometo_project01

    data_yaml = os.path.join(this_dir, "data.yaml")
    model_path = os.path.join(project_root, "yolov8n.pt")   # 루트에 있는 yolov8n.pt 사용

    model = YOLO(model_path)
    model.train(
        data=data_yaml,
        epochs=10,
        imgsz=640,
        project=os.path.join(project_root, "runs", "detect"),
        name="week3_multi"
    )

if __name__ == "__main__":
    main()