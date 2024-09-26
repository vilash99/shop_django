from datetime import date
from django import forms
from invoice.models import (
    Party, ItemService, Sale, Transaction, PartyBalance
)


class UpperField(forms.CharField):
    def to_python(self, value):
        return value.upper()


class PartyForm(forms.ModelForm):
    name = UpperField(label='Party name')
    phone = forms.CharField(label='Phone')
    address = forms.CharField(label='Address')
    balance_amount = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={'min': 0}),
        label='Balance Amount'
    )

    class Meta:
        model = Party
        exclude = ['id']

    def clean_name(self):
        """Check for same name for other ids"""
        tmp_name = self.cleaned_data.get('name')

        if Party.objects.filter(name=tmp_name).exclude(
                id=self.instance.id).exists():
            raise forms.ValidationError('Party Name is already exists.')
        return tmp_name


class ItemServiceForm(forms.ModelForm):
    name = UpperField(label='Name')
    price = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={'min': 0}),
        label='Price'
    )
    discount = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        initial=0.00,
        label='Discount'
    )

    def clean_name(self):
        """Check for same name for other ids"""
        tmp_name = self.cleaned_data.get('name')

        if ItemService.objects.filter(name=tmp_name).exclude(
                id=self.instance.id).exists():
            raise forms.ValidationError('This Item/Service is already exists.')
        return tmp_name


class ItemsForm(ItemServiceForm):
    quantity = forms.IntegerField(
        initial=1,
        widget=forms.NumberInput(attrs={'min': 1}),
        label='Quantity'
    )

    class Meta:
        model = ItemService
        exclude = ['id', 'item_type']


class ServiceForm(ItemServiceForm):
    class Meta:
        model = ItemService
        exclude = ['id', 'quantity', 'item_type']


class InvoiceForm(forms.ModelForm):
    bill_date = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Invoice date'
    )
    party = forms.ModelChoiceField(
        queryset=Party.objects.all().order_by('name'),
        label='Party name'
    )

    class Meta:
        model = Sale
        exclude = ['id']


class TransactionItemForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        queryset=ItemService.objects.filter(item_type=True).order_by('name'),
        label='Item Name'
    )
    price = forms.IntegerField(initial=0, label='Price')
    quantity = forms.IntegerField(initial=1, label='Quantity')
    amount = forms.IntegerField(initial=0, label='Amount')

    field_order = ['item', 'price', 'quantity', 'amount']

    class Meta:
        model = Transaction
        exclude = ['id', 'sales']


class TransactionServiceForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        queryset=ItemService.objects.filter(item_type=False).order_by('name'),
        label='Service Title',
    )
    amount = forms.IntegerField(initial=0, help_text='Amount')

    class Meta:
        model = Transaction
        exclude = ['id', 'price', 'sales', 'quantity']


class PartyBalanceForm(forms.ModelForm):
    party = forms.ModelChoiceField(
        queryset=Party.objects.all().order_by('name'),
        label='Party Name'
    )
    pay_date = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Payment Date'
    )
    amount = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={'min': 0}),
        label='Amount'
    )

    class Meta:
        model = PartyBalance
        exclude = ['id']

    def clean_amount(self):
        """Ensure that the amount is a positive value."""
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount
