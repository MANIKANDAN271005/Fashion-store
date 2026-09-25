from decimal import Decimal

from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    """Validates the custom admin panel's product form (price, stock and real image uploads)."""

    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'stock', 'is_available', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['stock'].required = False

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def clean_description(self):
        return (self.cleaned_data.get('description') or '').strip()

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < Decimal('0.01'):
            raise forms.ValidationError('Price must be greater than zero.')
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        return 0 if stock is None else stock


def form_error_messages(form):
    """Flatten form errors into readable strings for the messages framework."""
    errors = []
    for field, field_errors in form.errors.items():
        label = form.fields[field].label if field in form.fields else ''
        for error in field_errors:
            errors.append(f'{label}: {error}' if label else error)
    return errors
