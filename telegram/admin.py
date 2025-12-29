from django.contrib import admin
from .models import User, Massage, Chat
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
# برای فارسی سازی پنل ادمین
# _______________________

admin.site.site_header = "پنل ادمین"
admin.site.site_title = "پنل ادمین"
admin.site.index_title = "پنل مدیریت"


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ("username", "first_name", "email", "is_superuser" )
    fieldsets = BaseUserAdmin.fieldsets + (
    ('info', {'fields': ('birth_date', 'bio', 'photo_profile','phone_number')}),
    )

class MassageAdmin(admin.TabularInline):
    model = Massage
    xtra = 0
    ordering = ['create_at']
    readonly_fields = ['sender','text' , 'create_at']

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2')
    search_fields = ['user1__username', 'user2_username']
    inlines = [MassageAdmin]
