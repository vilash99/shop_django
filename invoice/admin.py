from django.contrib import admin
from invoice.models import (Profile, Party, ItemService, Sale,
                            Transaction)

admin.site.register(Profile)
admin.site.register(Party)
admin.site.register(ItemService)
admin.site.register(Sale)
admin.site.register(Transaction)
