from django.contrib import admin

from .models import (User,
                     Banner,
                     Category,
                     Product,
                     Order)


admin.site.register([User,
                     Banner,
                     Category,
                     Product,
                     Order])
