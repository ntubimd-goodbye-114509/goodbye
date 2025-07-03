from ultralytics import YOLO
import os
import cv2
import uuid
from django.conf import settings

model_path = os.path.join(os.path.dirname(__file__), 'best.pt')
model = YOLO(model_path)

def crop_detected_objects(image_path, output_folder):
    results = model(image_path)[0]
    orig = cv2.imread(image_path)

    # 確保指定資料夾存在
    os.makedirs(output_folder, exist_ok=True)

    cropped_paths = []

    for i, box in enumerate(results.boxes):
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        label = results.names[cls_id]

        cropped = orig[y1:y2, x1:x2]

        if cropped.shape[0] == 0 or cropped.shape[1] == 0:
            continue

        filename = f"{label}_{uuid.uuid4().hex[:8]}.jpg"
        save_path = os.path.join(output_folder, filename)
        cv2.imwrite(save_path, cropped)

        # 這裡只回傳檔名，或讓 view 決定完整相對路徑
        cropped_paths.append(filename)

    return cropped_paths
