from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PartyBalance


@receiver(post_save, sender=PartyBalance)
def update_party_balance_on_save(sender, instance, **kwargs):
    """
    Update the balance_amount of the related Party when a PartyBalance is saved or updated.
    """
    # Calculate the total balance for the party based on all PartyBalance records
    total_balance = PartyBalance.objects.filter(party=instance.party).aggregate(total=models.Sum('amount'))['total'] or 0
    # Update the party's balance_amount
    instance.party.balance_amount = total_balance
    instance.party.save()

@receiver(post_delete, sender=PartyBalance)
def update_party_balance_on_delete(sender, instance, **kwargs):
    """
    Update the balance_amount of the related Party when a PartyBalance is deleted.
    """
    # Calculate the total balance for the party after deletion
    total_balance = PartyBalance.objects.filter(party=instance.party).aggregate(total=models.Sum('amount'))['total'] or 0
    # Update the party's balance_amount
    instance.party.balance_amount = total_balance
    instance.party.save()
