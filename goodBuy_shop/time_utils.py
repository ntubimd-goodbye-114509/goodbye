from goodBuy_shop.models import *
from datetime import datetime

# -------------------------
# 時間格式轉換
# -------------------------
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"
# 時間格式轉換&NULL賦值
def timeFormatChange_now(t):
    # 如果已經是 datetime，就直接回傳
    if isinstance(t, datetime):  
        return t
    elif t:
        return datetime.strptime(t, DATETIME_FORMAT)
    else:
        return datetime.strptime(datetime.now().strftime(DATETIME_FORMAT), DATETIME_FORMAT)
    
def timeFormatChange_longtime(t):
    if t:
        return datetime.strptime(t, DATETIME_FORMAT)
    else:
        return datetime(9999, 12, 31, 23, 59, 59)