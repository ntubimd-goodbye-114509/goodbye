# core/decorators_shortcuts.py
from .decorators_base import object_exists_required, object_owner_required, blacklist_check
from django.contrib.auth import get_user_model
from goodBuy_shop.models import Shop, Product, ShopAnnouncement
from goodBuy_tag.models import Tag
from goodBuy_order.models import Order, Cart, PurchaseIntent
from goodBuy_want.models import Want

User = get_user_model()

# --- 基礎存在驗證 ---
shop_exists_required = object_exists_required(
    model=Shop,
    arg_name='shop_id',
    context_name='shop',
    deleted_check='auto',
    deleted_msg='這個商店已被刪除'
)

product_exists_required = object_exists_required(
    model=Product,
    arg_name='product_id',
    context_name='product',
    deleted_check='auto',
    deleted_msg='這個商品或商店已被刪除'
)

order_exists_required = object_exists_required(
    model=Order,
    arg_name='order_id',
    context_name='order',
    not_found_msg='找不到這個訂單'
)


tag_exists_required = object_exists_required(
    model=Tag,
    arg_name='tag_id',
    context_name='tag',
    not_found_msg='找不到這個Tag'
)

user_exists_required = object_exists_required(
    model=User,
    arg_name='user_id',
    context_name='user',
    not_found_msg='找不到使用者'
)

want_exists_required = object_exists_required(
    model=Want,
    arg_name='want_id',
    context_name='want',
    not_found_msg='找不到這個收物帖'
)

# --- 擁有者驗證 ---
shop_owner_required = object_owner_required(
    model=Shop,
    arg_name='shop_id',
    owner_field='owner',
    context_name='shop',
    not_found_msg='找不到商店',
    owner_error_msg='這不是您的商店哦',
    deleted_check='auto',
    deleted_msg='這個商店已被刪除'
)

product_owner_required = object_owner_required(
    model=Product,
    arg_name='product_id',
    owner_field='shop.owner',
    context_name='product',
    not_found_msg='找不到商品',
    owner_error_msg='這不是您的商品哦',
    deleted_check='auto',
    deleted_msg='這個商品或商店已被刪除'
)

want_owner_required = object_owner_required(
    model=Want,
    arg_name='post_id',
    owner_field='user',
    context_name='want',
    not_found_msg='找不到這篇收物帖',
    owner_error_msg='這不是您的收物帖喔',
    deleted_check='auto',
    deleted_msg='這篇收物帖已被刪除'
)

announcement_owner_required = object_owner_required(
    model=ShopAnnouncement,
    arg_name='announcement_id',
    owner_field='shop.owner',
    context_name='announcement',
    not_found_msg='找不到這則公告',
    owner_error_msg='這不是您商店的公告喔',
    deleted_check=lambda a: a.shop.permission_id == 3,
    deleted_msg='此公告所屬商店已被刪除'
)

# --- 黑名單組合 ---
def shop_exists_and_not_blacklisted():
    return lambda view_func: \
        blacklist_check(lambda shop: shop.owner, msg='你已被此賣家封鎖，無法查看')(\
            shop_exists_required(view_func))

def product_exists_and_not_blacklisted():
    return lambda view_func: \
        blacklist_check(lambda product: product.shop.owner, msg='你已被此賣家封鎖，無法查看')(\
            product_exists_required(view_func))

def user_exists_and_not_blacklisted():
    return lambda view_func: \
        blacklist_check(lambda user: user, msg='你已被此使用者封鎖，無法查看')(\
            user_exists_required(view_func))

def announcement_exists_and_shop_visible():
    return lambda view_func: \
        blacklist_check(lambda a: a.shop.owner, msg='你已被此賣家封鎖，無法查看')(\
            object_exists_required(
                model=ShopAnnouncement,
                arg_name='announcement_id',
                context_name='announcement',
                deleted_check=lambda a: a.shop.permission_id == 3,
                deleted_msg='此公告所屬商店已被刪除'
            )(view_func))