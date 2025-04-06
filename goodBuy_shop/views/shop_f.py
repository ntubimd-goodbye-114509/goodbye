from goodBuy_shop.models import *
from datetime import datetime

# 時間格式轉換&NULL賦值
def timeFormatChange_now(t):
    if t:
        return datetime.strptime(t, "%Y-%m-%dT%H:%M")
    else:
        return datetime.strptime(datetime.now(), "%Y-%m-%dT%H:%M")
    
def timeFormatChange_longtime(t):
    if t:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M")
    else:
        t = datetime(9999, 12, 31, 23, 59, 59)