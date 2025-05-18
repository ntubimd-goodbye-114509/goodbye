from django import forms
from django.forms.widgets import ClearableFileInput

from .models import Want, WantImg, WantTag
from goodBuy_tag.models import Tag
from goodBuy_shop.models import Permission

class MultipleClearableFileInput(ClearableFileInput):
    allow_multiple_selected = True

# -------------------------
# 收物帖創建/修改表單
# -------------------------
class WantForm(forms.ModelForm):
    tag_names = forms.CharField(required=False, widget=forms.HiddenInput())
    images = forms.FileField(
        required=False,
        widget=MultipleClearableFileInput(attrs={'multiple': True, 'class': 'form-control'})
    )
    cover_index = forms.IntegerField(required=False, widget=forms.HiddenInput())
    image_order = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Want
        fields = ['title', 'post_text','permission']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '輸入收物帖標題'}),
            'post_text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '輸入收物帖內容'}),
            'permission': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.is_edit = kwargs.get('instance') is not None
        super().__init__(*args, **kwargs)

        self.fields['permission'].queryset = Permission.objects.filter(id__in=[1, 2])

    def save(self, commit=True):
        want = super().save(commit=False)

        if self.user:
            want.user = self.user

        if commit:
            want.save()

            # 更新標籤
            tag_names = self.data.getlist('tag_names')
            existing_tags = Tag.objects.filter(name__in=tag_names)
            existing_names = set(existing_tags.values_list('name', flat=True))
            new_names = set(tag_names) - existing_names
            new_tags = [Tag.objects.create(name=name) for name in new_names]
            all_tags = list(existing_tags) + new_tags

            if self.is_edit:
                WantTag.objects.filter(want=want).exclude(tag__name__in=tag_names).delete()

            for tag in all_tags:
                WantTag.objects.get_or_create(want=want, tag=tag)

        return want

# -------------------------
# 收物帖圖片表單
# -------------------------
class WantImgForm(forms.ModelForm):
    class Meta:
        model = WantImg
        fields = ['img', 'is_cover']
        widgets = {
            'img': ClearableFileInput(attrs={'class': 'form-control'}),
        }
