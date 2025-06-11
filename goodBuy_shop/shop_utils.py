from django.db.models import *
from goodBuy_shop.models import *
from django.utils import timezone
from django.db.models.functions import Coalesce
# -------------------------
# shop回傳fk串接
# -------------------------
def shopInformation_many(shops):
    return (
        shops.annotate(
            total_stock=Sum(Case(When(product__stock__gt=0, then='product__stock'),default=0,output_field=IntegerField())),
            price_min=Coalesce(Min('product__price'), 0),
            price_max=Coalesce(Max('product__price'), 0),
        )
        .select_related('permission', 'shop_state', 'purchase_priority')
        .prefetch_related(
            Prefetch('shoppayment_set', queryset=ShopPayment.objects.select_related('payment_account')),
            Prefetch('shoptag_set', queryset=ShopTag.objects.select_related('tag')),
            Prefetch('images', queryset=ShopImg.objects.filter(is_cover=True)),
        )
    )