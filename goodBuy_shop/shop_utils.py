from django.db.models import *
from goodBuy_shop.models import *
# -------------------------
# shop回傳fk串接
# -------------------------
def shopInformation_many(shops):
        return (
        shops.annotate(total_stock=Sum(Case(When(product__stock__gt=0, then='product__stock'),default=0,output_field=IntegerField())))
        .select_related('permission', 'shop_state', 'purchase_priority')
        .prefetch_related(
            Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
            Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
            Prefetch('images', queryset=ShopImg.objects.filter(is_cover=True)),
        )
        .order_by('-total_stock', '-date')
    )