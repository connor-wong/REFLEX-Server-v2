import cv2
import time
import threading
import queue
from ultralytics import YOLO

# =====================
# CONFIG
# =====================
MODEL_PATH = "./Model_7n.pt"
CAMERA_ID = 1
IMG_SIZE = 320
DISPLAY_W = 720
DISPLAY_H = 1280

# =====================
# Helper
# =====================
def scale_and_crop(img, out_w, out_h):
    h, w = img.shape[:2]
    scale = max(out_w / w, out_h / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (nw, nh))
    x1 = (nw - out_w) // 2
    y1 = (nh - out_h) // 2
    return resized[y1:y1 + out_h, x1:x1 + out_w]

# =====================
# Threads
# =====================
def capture_thread(cap, frame_q, stop):
    while not stop.is_set():
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)  # mirror early

        if not frame_q.full():
            frame_q.put(frame)

def inference_thread(model, frame_q, result_q, stop):
    while not stop.is_set():
        try:
            frame = frame_q.get(timeout=0.1)
        except queue.Empty:
            continue

        results = model(frame, imgsz=IMG_SIZE, verbose=False)
        annotated = results[0].plot()

        if not result_q.full():
            result_q.put(annotated)

def display_thread(result_q, stop):
    cv2.namedWindow("YOLO Segmentation (Mirror)", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("YOLO Segmentation (Mirror)", DISPLAY_W, DISPLAY_H)

    last = time.time()
    frames = 0
    fps = 0.0

    while not stop.is_set():
        try:
            frame = result_q.get(timeout=0.1)
        except queue.Empty:
            continue

        frame = scale_and_crop(frame, DISPLAY_W, DISPLAY_H)

        frames += 1
        now = time.time()
        if now - last >= 1.0:
            fps = frames / (now - last)
            frames = 0
            last = now

        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2,
        )

        cv2.imshow("YOLO Segmentation (Mirror)", frame)
        if cv2.waitKey(1) & 0xFF in (27, ord("q")):
            stop.set()

    cv2.destroyAllWindows()

# =====================
# Main
# =====================
def main():
    model = YOLO(MODEL_PATH, task="segment")
    cap = cv2.VideoCapture(CAMERA_ID, apiPreference=cv2.CAP_DSHOW)

    frame_q = queue.Queue(maxsize=1)   # always newest frame
    result_q = queue.Queue(maxsize=1)

    stop = threading.Event()

    threads = [
        threading.Thread(target=capture_thread, args=(cap, frame_q, stop), daemon=True),
        threading.Thread(target=inference_thread, args=(model, frame_q, result_q, stop), daemon=True),
        threading.Thread(target=display_thread, args=(result_q, stop), daemon=True),
    ]

    for t in threads:
        t.start()

    try:
        while not stop.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop.set()

    cap.release()

if __name__ == "__main__":
    main()
