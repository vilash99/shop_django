from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from .models import PartyBalance, Transaction


@receiver(post_save, sender=PartyBalance)
def update_party_balance_on_save(sender, instance, created, **kwargs):
    """
    Update the balance_amount of the related Party when a PartyBalance is saved.
    """
    party = instance.party
    party.balance_amount = F('balance_amount') - instance.amount
    party.save(update_fields=['balance_amount'])

@receiver(post_delete, sender=PartyBalance)
def update_party_balance_on_delete(sender, instance, **kwargs):
    """
    Update the balance_amount of the related Party when a PartyBalance is deleted.
    """
    party = instance.party

    # Decrease the party's balance_amount by the amount of the deleted PartyBalance record
    party.balance_amount = F('balance_amount') + instance.amount
    party.save(update_fields=['balance_amount'])



@receiver(post_save, sender=Transaction)
def update_sale_total_amount(sender, instance, **kwargs):
    """
    Update the total_amount of the related Sale when a Transaction is saved or updated.
    """
    # Calculate the total_amount for the Invoice based on all Transaction records
    sale = instance.sales
    sale.total_amount = sum(transaction.amount for transaction in sale.transactions.all())
    sale.save()

@receiver(post_delete, sender=Transaction)
def update_sale_total_amount_on_delete(sender, instance, **kwargs):
    """
    Update the total_amount of the related Sale when a Transaction is deleted.
    """
    sale = instance.sales
    sale.total_amount = sum(transaction.amount for transaction in sale.transactions.all())
    sale.save()