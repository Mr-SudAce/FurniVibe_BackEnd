from django import forms
from django.contrib.auth import get_user_model
from .models import ProductModel, CategoryModel, BrandModel, ProductVariantModel, BlogModel

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
            "image",
            "is_active",
            "is_featured",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "brand": forms.Select(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "discount_percent": forms.NumberInput(attrs={"class": "form-control"}),
            "warranty_years": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = CategoryModel
        fields = ["name", "image", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class BrandForm(forms.ModelForm):
    class Meta:
        model = BrandModel
        fields = ["name", "logo", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "logo": forms.FileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariantModel
        fields = [
            "product", "model", "material", "color", 
            "weight_kg", "length", "width", "height", 
            "stock", "delivery_days", "is_made_to_order", "is_active"
        ]
        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "material": forms.TextInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "weight_kg": forms.NumberInput(attrs={"class": "form-control"}),
            "length": forms.TextInput(attrs={"class": "form-control"}),
            "width": forms.TextInput(attrs={"class": "form-control"}),
            "height": forms.TextInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "delivery_days": forms.NumberInput(attrs={"class": "form-control"}),
            "is_made_to_order": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class BlogForm(forms.ModelForm):
    class Meta:
        model = BlogModel
        fields = ["title", "image", "content", "is_active"]
        exclude = ["author"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }