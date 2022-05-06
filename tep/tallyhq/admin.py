from django.contrib import admin
from .models import *

admin.site.site_url = "/tallyhq/manageteachers/"  #THIS AFFECTS THE 'VIEW_SITE'  LINK IN DJANGO ADMIN

admin.site.register(Teacher)
admin.site.register(Item)
admin.site.register(School)
admin.site.register(Waiver)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ValidationPassword)

admin.site.site_header = "TEP Admin"
admin.site.index_title = "TEP Admin Controls"