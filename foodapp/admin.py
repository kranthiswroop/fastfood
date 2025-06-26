from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status')
    list_filter = ('status',)
    search_fields = ('user__username',)

from .models import MenuItem, Category, Profile

admin.site.register(MenuItem)
admin.site.register(Category)

admin.site.register(Profile)

