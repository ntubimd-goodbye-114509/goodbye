from django.core.management.base import BaseCommand
from django.utils import timezone
from goodBuy_shop.models import Shop
from goodBuy_order.models import Order, ProductOrder
from django.db import transaction
from collections import defaultdict
from .rush_utils import *

class Command(BaseCommand):
    help = "自動分配搶購商店的訂單（截團）"

    def handle(self, *args, **options):
        now = timezone.now()
        shops = Shop.objects.filter(
            purchase_priority_id__in=[2, 3],
            end_time__lt=now,
            is_rush_settled=False
        )

        for shop in shops:
            self.stdout.write(self.style.SUCCESS(f'正在處理商店：{shop.name}'))
            self.allocate_shop(shop)

    def allocate_shop(self, shop):
        intent_summaries = get_rush_summaries(shop)

        product_claimed = defaultdict(int)

        with transaction.atomic():
            for summary in intent_summaries:
                user = summary['user']
                order = Order.objects.create(
                    user=user,
                    shop=shop,
                    total=0,
                    payment_mode='full',
                    pay_state_id=1,
                    order_state_id=1,
                )
                total_price = 0
                for ip in summary['products']:
                    available = ip.product.stock - product_claimed[ip.product.id]
                    claim_qty = min(ip.quantity, available)

                    if claim_qty > 0:
                        ProductOrder.objects.create(
                            order=order,
                            product=ip.product,
                            amount=claim_qty,
                            product_name=ip.product.name,
                            product_price=ip.product.price,
                            product_img=ip.product.img.name if ip.product.img else '',
                        )
                        product_claimed[ip.product.id] += claim_qty
                        total_price += ip.product.price * claim_qty

                if total_price == 0:
                    order.delete()
                else:
                    order.total = total_price
                    order.save()

            shop.is_rush_settled = True
            shop.purchase_priority_id = 1
            shop.save(update_fields=['purchase_priority_id'])