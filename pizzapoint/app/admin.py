from django.contrib import admin

from .models import (User,
                     Banner,
                     Category,
                     Product,
                     OrderItem,
                     OrderItemRelation,
                     Order)


class OrderItemAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['user', 'total', 'status' ]
        return readonly_fields


class OrderAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['user', 'sum_total', 'order_items']
        return readonly_fields


admin.site.register([User,
                     Banner,
                     Category,
                     Product,
                     OrderItemRelation])
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)