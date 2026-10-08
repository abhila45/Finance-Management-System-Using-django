from django import forms
from .models import Transaction, Category

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["title", "amount", "transaction_type", "category", "date", "description", "tags", "currency"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "tags": forms.TextInput(attrs={"placeholder": "food, grocery, urgent"}),
            "currency": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user
            ) | Category.objects.filter(user__isnull=True)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "transaction_type"]