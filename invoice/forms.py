from datetime import date
from django import forms
from invoice.models import Profile, Party, ItemService, Sale, Transaction


class UpperField(forms.CharField):
    def to_python(self, value):
        return value.upper()


class ProfileForm(forms.ModelForm):
    name = forms.CharField(label='Company name')
    phone = forms.CharField(label='Phone number')
    address = forms.CharField(label='Address')
    reg_no = forms.CharField(label='GST number')

    class Meta:
        model = Profile
        exclude = ['id']


class PartyForm(forms.ModelForm):
    name = UpperField(label='Party name')
    phone = forms.CharField(label='Phone')
    address = forms.CharField(label='Address')

    class Meta:
        model = Party
        exclude = ['id']

    def clean_name(self):
        """Check for same name for other ids"""
        tmp_name = self.cleaned_data.get('name')

        if Party.objects.filter(name=tmp_name).exclude(
                id=self.instance.id).exists():
            raise forms.ValidationError('Name already exists.')
        return tmp_name


class ItemServiceForm(forms.ModelForm):
    name = UpperField(label='Name')
    price = forms.IntegerField(
        initial=0,
        widget=forms.TextInput(attrs={'min': 1, 'type': 'number'}),
        label='Price'
    )

    def clean_name(self):
        """Check for same name for other ids"""
        tmp_name = self.cleaned_data.get('name')

        if ItemService.objects.filter(name=tmp_name).exclude(
                id=self.instance.id).exists():
            raise forms.ValidationError('Item/Service already exists.')
        return tmp_name


class ItemsForm(ItemServiceForm):
    quantity = forms.IntegerField(
        initial=1,
        widget=forms.TextInput(attrs={'min': 1, 'type': 'number'}),
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
        queryset=Party.objects.all(),
        label='Party name'
    )

    class Meta:
        model = Sale
        exclude = ['id']


class TransactionItemForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        queryset=ItemService.objects.filter(item_type=True),
        label='Item name'
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
        queryset=ItemService.objects.filter(item_type=False),
        label='Service title',
    )
    amount = forms.IntegerField(initial=0, help_text='Amount')

    class Meta:
        model = Transaction
        exclude = ['id', 'price', 'sales', 'quantity']
