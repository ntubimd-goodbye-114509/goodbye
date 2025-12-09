import numpy as np
from ultralytics import YOLO
import os
import cv2
import uuid
from django.conf import settings


model_path = os.path.join(os.path.dirname(__file__), 'best.pt')
model = YOLO(model_path)

# def crop_detected_objects(image_path, output_folder):
#     results = model(image_path)[0]
#     orig = cv2.imread(image_path)

#     # 確保指定資料夾存在
#     os.makedirs(output_folder, exist_ok=True)

#     cropped_paths = []

#     for i, box in enumerate(results.boxes):
#         x1, y1, x2, y2 = map(int, box.xyxy[0])
#         cls_id = int(box.cls[0])
#         label = results.names[cls_id]

#         cropped = orig[y1:y2, x1:x2]

#         if cropped.shape[0] == 0 or cropped.shape[1] == 0:
#             continue

#         filename = f"{label}_{uuid.uuid4().hex[:8]}.jpg"
#         save_path = os.path.join(output_folder, filename)
#         cv2.imwrite(save_path, cropped)

#         # 這裡只回傳檔名，或讓 view 決定完整相對路徑
#         cropped_paths.append(filename)

#     return cropped_paths

#針對整張圖進行透視矯正
def correct_full_image_perspective(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return img

    largest = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(largest)
    box = cv2.boxPoints(rect).astype(int)

    # 依照 minAreaRect 取 w,h
    w = int(rect[1][0])
    h = int(rect[1][1])
    if w == 0 or h == 0:
        return img

    # 對應原圖座標
    src_pts = np.float32(box)

    # 定義矯正後的區域座標
    dst_pts = np.float32([
        [0, 0],
        [w - 1, 0],
        [w - 1, h - 1],
        [0, h - 1]
    ])

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    orig = cv2.warpPerspective(img, M, (w, h))

    return orig

# 針對整張圖矯正後再做偵測與裁切
def crop_detected_objects(image_path, output_folder):
    orig = cv2.imread(image_path)

    # 這裡改為整張圖矯正（關鍵）
    # corrected = correct_full_image_perspective(orig)

    # 用矯正後的影像做 YOLO 偵測（非常重要）
    results = model(orig)[0]

    os.makedirs(output_folder, exist_ok=True)
    cropped_paths = []

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        label = results.names[cls_id]

        cropped = orig[y1:y2, x1:x2]
        if cropped.size == 0:
            continue

        filename = f"{label}_{uuid.uuid4().hex[:8]}.jpg"
        save_path = os.path.join(output_folder, filename)
        cv2.imwrite(save_path, cropped)

        cropped_paths.append(filename)

    return cropped_paths

# '''
# 以下為測試影像圖片處理
# 雖可用但仍有bug，暫不啟用
# '''
# # ========= 亮度 / 對比（CLAHE） =========
# def auto_contrast_clahe(img):
#     """
#     LAB + CLAHE 提升亮度與對比
#     img: BGR 圖片 (np.ndarray)
#     """
#     lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
#     L, A, B = cv2.split(lab)

#     # clipLimit / tileGridSize 可再調整
#     clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
#     L2 = clahe.apply(L)

#     lab2 = cv2.merge((L2, A, B))
#     result = cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)
#     return result

# # ========= 彩度提升 =========
# def boost_saturation(img, factor=1.1):
#     """
#     提升彩度（飽和度），避免過灰
#     factor > 1 比較鮮豔
#     """
#     hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype("float32")
#     h, s, v = cv2.split(hsv)

#     s *= factor
#     s = np.clip(s, 0, 255)

#     hsv_merged = cv2.merge((h, s, v))
#     result = cv2.cvtColor(hsv_merged.astype("uint8"), cv2.COLOR_HSV2BGR)
#     return result


# # ========= 透視矯正 =========
# def correct_full_image_perspective(img):
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     blur = cv2.GaussianBlur(gray, (5,5), 0)
#     thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#     contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     if len(contours) == 0:
#         return img

#     largest = max(contours, key=cv2.contourArea)
#     rect = cv2.minAreaRect(largest)
#     box = cv2.boxPoints(rect).astype(int)

#     w = int(rect[1][0])
#     h = int(rect[1][1])
#     if w == 0 or h == 0:
#         return img

#     src_pts = np.float32(box)

#     dst_pts = np.float32([
#         [0, 0],
#         [w - 1, 0],
#         [w - 1, h - 1],
#         [0, h - 1]
#     ])

#     M = cv2.getPerspectiveTransform(src_pts, dst_pts)
#     orig = cv2.warpPerspective(img, M, (w, h))

#     return orig


# # ========= 圖片前處理（亮度 + 光照 + 彩度） =========
# def preprocess_uploaded_image(img):
#     #1亮度/對比修正
#     enhanced = auto_contrast_clahe(img)
#     #2 略微提高彩度
#     enhanced = boost_saturation(enhanced, factor=1.1)

#     return enhanced


# # ========= YOLO 偵測 + 裁切 =========
# def crop_detected_objects(image_path, output_folder):
#     orig = cv2.imread(image_path)
#     if orig is None:
#         raise ValueError(f"讀不到圖片: {image_path}")

#     # 上傳後自動做亮度＋彩度修正
#     preprocessed = preprocess_uploaded_image(orig)
#     preprocessed = correct_full_image_perspective(preprocessed)
    
#     # 用處理後的圖片做 YOLO 偵測
#     results = model(preprocessed)[0]

#     os.makedirs(output_folder, exist_ok=True)
#     cropped_paths = []

#     h, w = preprocessed.shape[:2]

#     for box in results.boxes:
#         x1, y1, x2, y2 = map(int, box.xyxy[0])

#         # 防守式寫法：避免超出邊界
#         x1 = max(0, min(x1, w - 1))
#         x2 = max(0, min(x2, w - 1))
#         y1 = max(0, min(y1, h - 1))
#         y2 = max(0, min(y2, h - 1))
#         if x2 <= x1 or y2 <= y1:
#             continue

#         cls_id = int(box.cls[0])
#         label = results.names[cls_id]

#         cropped = preprocessed[y1:y2, x1:x2]
#         if cropped.size == 0:
#             continue

#         filename = f"{label}_{uuid.uuid4().hex[:8]}.jpg"
#         save_path = os.path.join(output_folder, filename)
#         cv2.imwrite(save_path, cropped)
#         cropped_paths.append(filename)

#     return cropped_paths
