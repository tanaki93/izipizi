from django.contrib import admin

from projects_app.models import Order, OrderItem, OrderItemComment, OrderPackage, CommentImage, OrderPacket, \
    PacketProduct, Flight

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderPackage)
admin.site.register(OrderItemComment)
admin.site.register(CommentImage)
admin.site.register(OrderPacket)
admin.site.register(Flight)
admin.site.register(PacketProduct)




