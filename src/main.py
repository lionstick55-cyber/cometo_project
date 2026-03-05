import cv2

def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # ✅ MSMF 대신 DSHOW
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    while True:
        ok, frame = cap.read()
        if not ok:
            print("❌ Failed to read frame")
            break

        frame = cv2.flip(frame, 1)  # 좌우반전

        cv2.imshow("Focus AI", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()