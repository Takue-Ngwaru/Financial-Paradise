from django.contrib import admin

from .models import *

admin.site.register(Account)
admin.site.register(Owner)
admin.site.register(Transaction)
admin.site.register(Vehicle)
admin.site.register(Deposit)
