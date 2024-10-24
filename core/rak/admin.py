# rak/admin.py

from django.contrib import admin
from .models import RandomActOfKindness, Claimant, Notification, PayItForward

admin.site.register(RandomActOfKindness)
admin.site.register(Claimant)
# admin.site.register(RAKClaim)
admin.site.register(Notification)
admin.site.register(PayItForward)
