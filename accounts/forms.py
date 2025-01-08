from django import forms
from .models import  CustomUser

class CustomAuthenticationForm(forms.ModelForm):
    username = forms.EmailField(label="Email", max_length=254)

    class Meta:
        model = CustomUser
        fields = ['email', 'password']