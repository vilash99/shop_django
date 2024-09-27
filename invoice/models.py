from datetime import date
from django.db import models
from django.urls import reverse



class Profile(models.Model):
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=128)
    reg_no = models.CharField(max_length=50, verbose_name="Registration Number")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('invoice:profile', kwargs={'pk': self.pk})


class Party(models.Model):
    name = models.CharField(max_length=80, unique=True)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=128)
    balance_amount = models.IntegerField(default=0, verbose_name="Balance Amount")

    class Meta:
        verbose_name_plural = 'Parties'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('invoice:parties')


class PartyBalance(models.Model):
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="balances")
    pay_date = models.DateField(default=date.today, verbose_name="Payment Date")
    amount = models.IntegerField(default=0)

    def __str__(self):
        return "{} - {} on {}".format(self.party.name, self.amount, self.pay_date)

    def get_absolute_url(self):
        return reverse('invoice:party_detail', kwargs={'pk': self.party.pk})


class ItemService(models.Model):
    ITEM = True
    SERVICE = False
    ITEM_TYPE_CHOICES = [
        (ITEM, 'Item'),
        (SERVICE, 'Service'),
    ]

    name = models.CharField(max_length=128, unique=True)
    item_type = models.BooleanField(default=ITEM, choices=ITEM_TYPE_CHOICES, verbose_name="Type")
    quantity = models.PositiveIntegerField(default=0, help_text="Set to 0 if service")
    price = models.PositiveIntegerField(default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        verbose_name_plural = 'Items & Services'

    def __str__(self):
        return self.name


class Sale(models.Model):
    bill_date = models.DateField(default=date.today, verbose_name="Bill Date")
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="sales")

    def __str__(self):
        return "Sale on {} - {}".format(self.bill_date, self.party.name)

    def get_absolute_url(self):
        return reverse('invoice:transaction', kwargs={'p_id': self.pk})


class Transaction(models.Model):
    sales = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="transactions")
    item = models.ForeignKey(ItemService, on_delete=models.CASCADE, related_name="transactions")
    price = models.PositiveIntegerField(default=0)
    quantity = models.IntegerField(default=0, help_text="Set to 0 if service")
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{} - {}".format(self.item.name, self.sale.party.name)

    @property
    def item_type(self):
        return "Item" if self.item.item_type else "Service"





