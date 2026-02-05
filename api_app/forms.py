from django import forms
from django.contrib.auth import get_user_model
from .models import ProductModel

User = get_user_model()

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        
        # Auto-generate username: firstname + lastname + number if needed
        base_username = f"{self.cleaned_data['first_name']}{self.cleaned_data['last_name']}".lower()
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username
        
        # Default role: Admin (not superadmin)
        user.is_staff = True
        user.is_superuser = False
        user.is_user = False

        if commit:
            user.save()
        return user


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = [
            "name",
            "category",
            "brand",
            "price",
            "discount_percent",
            "warranty_years",
            "description",
        ]