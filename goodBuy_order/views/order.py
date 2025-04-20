from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import Product, Order, ProductOrder
from ..order_forms import OrderCreateForm

@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, request.FILES)
        product_ids = request.POST.getlist('product_ids')
        quantities = request.POST.getlist('quantities')

        if form.is_valid() and product_ids:
            # 取得第一個商品所屬的 shop（假設同一訂單內商品來自同一商店）
            first_product = get_object_or_404(Product, id=product_ids[0])
            shop = first_product.shop

            order = form.save(commit=False)
            order.user = request.user
            order.shop = shop
            order.total = 0  # 等會計算
            order.save()

            total_price = 0
            for pid, qty in zip(product_ids, quantities):
                product = get_object_or_404(Product, id=pid)
                subtotal = product.price * int(qty)
                total_price += subtotal

                ProductOrder.objects.create(
                    order=order,
                    product=product,
                    amount=qty,
                    product_name=product.name,
                    product_price=product.price,
                    product_img=product.img.name if product.img else ''
                )

            order.total = total_price
            order.save()

            messages.success(request, '訂單建立成功')
            return redirect('order_detail', order_id=order.id)
        else:
            messages.error(request, '訂單建立失敗，請檢查輸入資料')
    else:
        form = OrderCreateForm()
        # 可以加預選商品邏輯（例如購物車）傳給 template
        selected_products = []

    return render(request, 'order_form.html', {
        'form': form,
        # 'selected_products': selected_products ← 你可從購物車或前一頁帶入
    })
