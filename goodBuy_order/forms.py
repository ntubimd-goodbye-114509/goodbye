from django import forms
from .models import Order

from django import forms
from goodBuy_order.models import Order, UserAddress, Payment, PaymentAccount

# forms.py
from django import forms
from goodBuy_order.models import Order, UserAddress, Payment, PaymentAccount

class OrderForm(forms.ModelForm):
    address = forms.ModelChoiceField(
        queryset=UserAddress.objects.none(),
        label="收件地址",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    payment_method = forms.ChoiceField(
        choices=[],
        label="付款方式",
        widget=forms.RadioSelect
    )

    payment_account = forms.ModelChoiceField(
        queryset=PaymentAccount.objects.none(),
        required=False,
        label="匯款帳戶",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    payment_mode = forms.ChoiceField(
        choices=[('full', '全額付款'), ('deposit', '定金＋尾款')],
        required=False,
        label="付款機制",
        widget=forms.RadioSelect
    )

    class Meta:
        model = Order
        fields = ['address', 'payment_method', 'payment_account', 'payment_mode']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        shop = kwargs.pop('shop', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['address'].queryset = UserAddress.objects.filter(user=user)

        if shop:
            # 可用付款方式（若商店有匯款帳戶才顯示匯款）
            payment_choices = [('1', '取貨付款')]
            remittance_accounts = PaymentAccount.objects.filter(user=shop.owner)
            if remittance_accounts.exists():
                payment_choices.append(('remit', '匯款（銀行）'))

                self.fields['payment_account'].queryset = remittance_accounts
            else:
                self.fields['payment_account'].widget = forms.HiddenInput()

            self.fields['payment_method'].choices = payment_choices

            # 若不支援定金尾款則隱藏付款機制選項
            if not shop.deposit:
                self.fields['payment_mode'].widget = forms.HiddenInput()
                self.fields['payment_mode'].required = False
