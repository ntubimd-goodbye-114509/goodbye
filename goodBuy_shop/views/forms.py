from django import forms
from goodBuy_shop.models import *
from goodBuy_tag.models import *
from goodBuy_web.models import *

from django import forms
from goodBuy_shop.models import *
from goodBuy_tag.models import *
from goodBuy_web.models import *
from .time_f import *

class ShopForm(forms.ModelForm):
    payment_ids = forms.ModelMultipleChoiceField(
        queryset=PaymentAccount.objects.none(),  # 後面在 __init__ 補上
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    tag_ids = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2-tags'})
    )
    start_time = forms.TimeField(input_formats=['%H:%M'], required=False)
    end_time = forms.TimeField(input_formats=['%H:%M'], required=False)

    class Meta:
        model = Shop
        fields = [
            'name', 'introduce', 'start_time', 'end_time',
            'shop_state', 'permission', 'purchase_priority'
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.is_edit = kwargs.get('instance') is not None
        super().__init__(*args, **kwargs)

        # 排序：已綁定的付款帳戶優先
        if self.user:
            all_accounts = PaymentAccount.objects.all()
            user_accounts = self.user.payment_accounts.all()
            sorted_accounts = sorted(
                all_accounts,
                key=lambda acc: acc not in user_accounts
            )
            self.fields['payment_ids'].queryset = PaymentAccount.objects.filter(id__in=[acc.id for acc in sorted_accounts])

        # 如果是編輯，載入原本的多對多選項作為 initial
        if self.instance and self.instance.pk:
            self.fields['payment_ids'].initial = self.instance.paymentaccount_set.values_list('id', flat=True)
            self.fields['tag_ids'].initial = self.instance.tag_set.values_list('id', flat=True)

    def save(self, commit=True):
        shop = super().save(commit=False)

        # 預設時間
        if shop.start_time is None:
            shop.start_time = timeFormatChange_now()
        if shop.end_time is None:
            shop.end_time = timeFormatChange_longtime()

        if self.user:
            shop.owner = self.user

        if commit:
            shop.save()

            # 處理付款帳戶（多對多）
            payment_ids = set(self.cleaned_data.get('payment_ids').values_list('id', flat=True))
            old_payment_ids = set(ShopPayment.objects.filter(shop=shop).values_list('payment_account_id', flat=True))

            if self.is_edit:
                # 修改：刪除多餘的 + 新增新的
                for pid in payment_ids - old_payment_ids:
                    ShopPayment.objects.create(shop=shop, payment_account_id=pid)
                ShopPayment.objects.filter(shop=shop, payment_account_id__in=(old_payment_ids - payment_ids)).delete()
            else:
                # 新增：直接建立
                for pid in payment_ids:
                    ShopPayment.objects.create(shop=shop, payment_account_id=pid)

            # 處理標籤（多對多）
            tag_names = self.data.getlist('tag_ids')  # 這裡是名稱而非 id（因為有可能是新建的）
            existing_tags = Tag.objects.filter(name__in=tag_names)
            existing_names = set(existing_tags.values_list('name', flat=True))
            new_names = set(tag_names) - existing_names
            new_tags = [Tag.objects.create(name=name) for name in new_names]
            all_tags = list(existing_tags) + new_tags

            if self.is_edit:
                ShopTag.objects.filter(shop=shop).exclude(tag__name__in=tag_names).delete()

            for tag in all_tags:
                ShopTag.objects.get_or_create(shop=shop, tag=tag)

        return shop

class ShopImgForm(forms.ModelForm):
    class Meta:
        model = ShopImg
        fields = ['img', 'is_cover']
        widgets = {
            'img': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = ShopAnnouncement
        fields = ['title', 'announcement']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '輸入公告標題'
            }),
            'announcement': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '輸入公告內容...'
            })
        }
        labels = {
            'title': '公告標題',
            'announcement': '公告內容'
        }
