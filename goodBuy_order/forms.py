from django import forms
from .models import Order
from goodBuy_web.models import UserAddress
from goodBuy_order.models import OrderPayment

from django import forms
from goodBuy_order.models import Order

# -------------------------
# 訂單新增 地址、付款方式選擇
# -------------------------
class OrderForm(forms.ModelForm):
    PAYMENT_METHOD_CHOICES = [
        ('cash_on_delivery', '取貨付款'),
        ('remittance', '匯款')
    ]

    PAYMENT_MODE_CHOICES = [
        ('full', '一次付款'),
        ('split', '定金＋尾款')
    ]

    address = forms.ModelChoiceField(
        queryset=UserAddress.objects.none(),
        label="收件地址",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        label="付款方式",
        widget=forms.RadioSelect
    )

    payment_mode = forms.ChoiceField(
        choices=PAYMENT_MODE_CHOICES,
        required=False,
        label="付款機制",
        widget=forms.RadioSelect
    )
    class Meta:
        model = Order
        fields = ['address', 'payment_mode']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        shop = kwargs.pop('shop', None)
        shop_list = kwargs.pop('shop_list', None)

        super().__init__(*args, **kwargs)

        self.fields['payment_mode'].initial = 'full'

        if user:
            self.fields['address'].queryset = UserAddress.objects.filter(user=user)

        if shop_list:
            has_non_rush = any(shop.purchase_priority_id == 1 for shop in shop_list)
            if not has_non_rush:
                self.fields['address'].widget = forms.HiddenInput()
                self.fields['address'].required = False
                self.files['payment_method'].widget = forms.HiddenInput()
                self.fields['payment_method'].required = False
                self.files['payment_mode'].widget = forms.HiddenInput()
                self.fields['payment_mode'].required = False

        elif shop:
            if shop.purchase_priority_id != 1:
                self.fields['address'].widget = forms.HiddenInput()
                self.fields['address'].required = False

        if shop and not shop.deposit:
            self.fields['payment_mode'].widget = forms.HiddenInput()
            self.fields['payment_mode'].required = False
# -------------------------
# 上傳付款憑證
# -------------------------
class OrderPaymentForm(forms.ModelForm):
    class Meta:
        model = OrderPayment
        fields = ['amount', 'pay_proof', 'remark']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '請輸入匯款金額',
                'min': 1
            }),
            'pay_proof': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'remark': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '其他備註（可選）'
            }),
        }
        labels = {
            'amount': '匯款金額',
            'pay_proof': '匯款憑證上傳',
            'remark': '備註',
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('金額必須大於 0')
        return amount
