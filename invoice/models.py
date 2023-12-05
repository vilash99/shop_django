from datetime import date
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=128)
    reg_no = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('invoice:profile', kwargs={'pk': 1})


class Party(models.Model):
    name = models.CharField(max_length=80, unique=True)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = 'Parties'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('invoice:parties')


class ItemService(models.Model):
    name = models.CharField(max_length=128, unique=True)
    # item_type: True = Items, False = Services
    item_type = models.BooleanField(default=True)

    # Set total_qty=0 if item_type=False(Services)
    quantity = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Items & Services'


class Sale(models.Model):
    bill_date = models.DateField(default=date.today)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.bill_date)

    def get_absolute_url(self):
        return f"/invoice/{self.pk}"


class Transaction(models.Model):
    sales = models.ForeignKey(Sale, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemService, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)

    # Set item_qty 0 if item type is services
    quantity = models.IntegerField(default=0)
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.item.name

    @property
    def item_type(self):
        return self.item.item_type
