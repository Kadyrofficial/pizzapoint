from django.contrib import admin

from .models import (User,
                     Banner,
                     Category,
                     Product,
                     OrderItem,
                     Order)


admin.site.register([User,
                     Banner,
                     Category,
                     Product,
                     OrderItem,
                     Order])
