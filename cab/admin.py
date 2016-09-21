from django.contrib import admin
from cab.models import Cabs

class CabsAdmin(admin.ModelAdmin):
  list_display = ('cab_number', 'car_name', 'car_pink')
  list_filter = ['cab_number', 'car_pink']
  search_fields = ['cab_number', 'car_pink']
  
admin.site.register(Cabs, CabsAdmin)
