from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_method']  # 移除 pay_proof 和 second_supplement
        widgets = {
            'payment_method': forms.TextInput(attrs={'class': 'form-control'}),
        }