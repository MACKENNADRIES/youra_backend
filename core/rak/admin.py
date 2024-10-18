# rak/admin.py

from django.contrib import admin
from .models import RandomActOfKindness, RAKClaim, Notification, PayItForward

admin.site.register(RandomActOfKindness)
admin.site.register(RAKClaim)
admin.site.register(Notification)
admin.site.register(PayItForward)
