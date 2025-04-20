from django import forms
from goodBuy_shop.models import *
from goodBuy_tag.models import *
from goodBuy_web.models import *

from django import forms
from goodBuy_shop.models import *
from goodBuy_tag.models import *
from goodBuy_web.models import *
from .views.time_f import *

class ShopForm(forms.ModelForm):
    payment_ids = forms.ModelMultipleChoiceField(queryset=PaymentAccount.objects.none(), required=False, widget=forms.CheckboxSelectMultiple)
    tag_names = forms.CharField(required=False, widget=forms.HiddenInput())
    images = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}))
    cover_index = forms.IntegerField(required=False, widget=forms.HiddenInput())
    image_order = forms.CharField(required=False, widget=forms.HiddenInput())
    start_time = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        required=False
    )
    end_time = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        required=False
    )

    class Meta:
        model = Shop
        fields = ['name', 'introduce', 'start_time', 'end_time', 'shop_state', 'permission', 'purchase_priority', 'deposit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '輸入商店名稱'}),
            'introduce': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '輸入商店介紹'}),
            'deposit': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.is_edit = kwargs.get('instance') is not None
        super().__init__(*args, **kwargs)

        if self.user:
            all_accounts = PaymentAccount.objects.all()
            user_accounts = self.user.payment_accounts.all()
            sorted_accounts = sorted(all_accounts, key=lambda acc: acc not in user_accounts)
            self.fields['payment_ids'].queryset = PaymentAccount.objects.filter(id__in=[acc.id for acc in sorted_accounts])

        if self.instance and self.instance.pk:
            self.fields['payment_ids'].initial = self.instance.payment_account_set.values_list('id', flat=True)

    def save(self, commit=True):
        shop = super().save(commit=False)

        if shop.start_time is None:
            shop.start_time = timeFormatChange_now()
        if shop.end_time is None:
            shop.end_time = timeFormatChange_longtime()
        if self.user:
            shop.owner = self.user

        if commit:
            shop.save()

            # 處理付款
            payment_ids = set(self.cleaned_data.get('payment_ids').values_list('id', flat=True))
            old_payment_ids = set(ShopPayment.objects.filter(shop=shop).values_list('payment_account_id', flat=True))
            if self.is_edit:
                for pid in payment_ids - old_payment_ids:
                    ShopPayment.objects.create(shop=shop, payment_account_id=pid)
                ShopPayment.objects.filter(shop=shop, payment_account_id__in=(old_payment_ids - payment_ids)).delete()
            else:
                for pid in payment_ids:
                    ShopPayment.objects.create(shop=shop, payment_account_id=pid)

            # 處理標籤
            tag_names = self.data.getlist('tag_names')
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
