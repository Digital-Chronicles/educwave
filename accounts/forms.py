from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django import forms
from .models import  CustomUser

class CustomAuthenticationForm(forms.ModelForm):
    username = forms.EmailField(label="Email", max_length=254)

    class Meta:
        model = CustomUser
        fields = ['email', 'password']
        
        from django import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'role')  # Exclude username if not needed


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'role', 'is_active', 'is_staff')
