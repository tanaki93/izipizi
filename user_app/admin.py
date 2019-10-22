from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token

from user_app.models import User, ClientProfile, ConfirmationCode

admin.site.unregister(Group)
admin.site.unregister(Token)


class ClientInline(admin.StackedInline):
    model = ClientProfile
    extra = 1


class UserAdmin(admin.ModelAdmin):
    model = User

    list_display = ['username', 'user_type', 'last_login']
    inlines = [ClientInline]


admin.site.register(User, UserAdmin)
admin.site.register(ConfirmationCode)
