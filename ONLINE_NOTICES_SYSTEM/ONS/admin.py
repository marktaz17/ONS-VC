from django.contrib import admin
from .models import building_record,holidays,Signatories
# Register your models here.


admin.site.register(building_record)
admin.site.register(holidays)
admin.site.register(Signatories)

