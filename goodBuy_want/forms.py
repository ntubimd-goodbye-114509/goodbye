from django import forms
from .models import Want, wantImg, Tag, WantTag

class WantForm(forms.ModelForm):
    tag_names = forms.CharField(required=False, widget=forms.HiddenInput())
    images = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}))
    cover_index = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Want
        fields = ['title', 'post_text']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '輸入需求標題'}),
            'post_text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '輸入需求內容'})
        }

    def save(self, commit=True, user=None):
        want = super().save(commit=False)
        if user:
            want.user = user
        if commit:
            want.save()

            # 標籤處理
            tag_names = self.data.getlist('tag_names')
            existing_tags = Tag.objects.filter(name__in=tag_names)
            existing_names = set(existing_tags.values_list('name', flat=True))
            new_names = set(tag_names) - existing_names
            new_tags = [Tag.objects.create(name=name) for name in new_names]
            all_tags = list(existing_tags) + new_tags

            WantTag.objects.filter(want=want).exclude(tag__name__in=tag_names).delete()
            for tag in all_tags:
                WantTag.objects.get_or_create(want=want, tag=tag)

        return want


class WantImgForm(forms.ModelForm):
    class Meta:
        model = wantImg
        fields = ['img', 'is_cover']
        widgets = {
            'img': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
