import schedule
import time
import os

def run_clear_cropped_images():
    print("▶ 清理裁切暫存圖...")
    os.system("python manage.py clear_temp_images")

def run_settle_rush_orders():
    print("▶ 處理搶購商店分配...")
    os.system("python manage.py auto_allocate_rush_orders")

# 設定排程
schedule.every().hour.at(":00").do(run_clear_cropped_images)     # 每小時清除三個鐘頭內未操作的裁切暫存圖
schedule.every().hour.at(":00").do(run_settle_rush_orders)       # 每小時整點處理 rush shop

# 持續執行
if __name__ == "__main__":
    print("自動排程器已啟動...")
    while True:
        schedule.run_pending()
        time.sleep(60)
