from django.contrib import admin

from projects_app.models import Order, OrderItem, OrderItemComment, OrderPackage, CommentImage

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderPackage)
admin.site.register(OrderItemComment)
admin.site.register(CommentImage)




