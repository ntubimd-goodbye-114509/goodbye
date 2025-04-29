from django import forms
from .models import Product

# -------------------------
# 商品新增form
# -------------------------
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'amount', 'introduce', 'img']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'introduce': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'img': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
