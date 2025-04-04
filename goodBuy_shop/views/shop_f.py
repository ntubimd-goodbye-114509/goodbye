from goodBuy_shop.models import *
from datetime import datetime

# 全部商店時間排序
# homepage無演算法暫用
def allShopByUpdate():
    shops = Shop.objects.filter(permission=1).order_by('date', 'name')
    return shops

def search_shop():
    shops_by_name = Shop.objects.filter(name__icontains=kw)
    shops_by_tag = Shop.objects.filter(
            id__in=Shop_Tag.objects.filter(tag__name__icontains=kw).values_list('shop_id', flat=True)
        )
    shops = (shops_by_name | shops_by_tag).distinct()

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