from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import *

@login_required
def payment_accounts(request):
    user = request.user
    payments = Payment.objects.all()
    accounts = PaymentAccount.active.filter(user=user)

    if request.method == "POST":
        action = request.POST.get("action")

        # 新增付款方式帳號
        if action == "add":
            payment_id = request.POST.get("payment_id")
            account = request.POST.get("account")
            img = request.FILES.get("img")

            if payment_id and account:
                PaymentAccount.objects.create(
                    user=user,
                    payment_id=payment_id,
                    account=account,
                    img=img
                )
                messages.success(request, "付款方式新增成功")

        # 修改付款方式帳號
        elif action == "edit":
            account_id = request.POST.get("account_id")
            new_account = request.POST.get("account")
            new_img = request.FILES.get("img")
            payment_id = request.POST.get("payment_id")

            acc_obj = get_object_or_404(PaymentAccount, pk=account_id, user=user, is_delete=False)
            acc_obj.account = new_account
            if new_img:
                acc_obj.img = new_img
            if payment_id:
                acc_obj.payment_id = payment_id
            acc_obj.save()
            messages.success(request, "付款方式修改成功")

        # 刪除付款方式帳號（軟刪除）
        elif action == "remove":
            account_id = request.POST.get("account_id")
            acc_obj = get_object_or_404(PaymentAccount, pk=account_id, user=user, is_delete=False)
            acc_obj.is_delete = True
            acc_obj.save()
            messages.success(request, "付款方式已刪除")

        return redirect('payment_accounts')

    return render(request, 'common/payment.html', {
        'accounts': accounts,
        'payments': payments,
    })
