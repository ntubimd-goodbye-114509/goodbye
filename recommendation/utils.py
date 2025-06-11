from django.db.models import Q

# -------------------------
# 商店是否截止
# -------------------------
def shop_is_active(now):
    return Q(end_time__isnull=True) | Q(end_time__gt=now)