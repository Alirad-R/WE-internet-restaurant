# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CustomerProfile, OTP

class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (CustomerProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'country', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'city', 'country')
    list_filter = ('created_at', 'country', 'city')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(User, UserAdmin)
admin.site.register(OTP)