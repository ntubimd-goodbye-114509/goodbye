from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['pay_state', 'order_state', 'second_supplement', 'pay_proof']
        widgets = {
            'second_supplement': forms.NumberInput(attrs={'class': 'form-control'}),
            'pay_proof': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
