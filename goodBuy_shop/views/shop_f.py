from goodBuy_shop.models import Shop

# 全部商店時間排序
# homepage無演算法暫用
def allShopByUpdate():
    shops = Shop.objects.filter(permission=1).order_by('date', 'name')
    return shops

# user_id查詢
def shopById_many(user_id):
    shops = Shop.objects.filter(id=user_id)
    return shops

