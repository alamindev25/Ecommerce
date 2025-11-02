from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import PhoneOTP

admin.site.register(PhoneOTP)

class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ('phone', 'business_type', 'role', 'first_login', 'active', 'timestamp')
    list_filter = ('is_staff', 'is_admin', 'is_active', 'role', 'business_type')  # Add more filters if needed

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2'),
        }),
    )

    search_fields = ('phone', 'role', 'business_type')  # Include other fields if you want to search by them
    ordering = ('phone',)
    filter_horizontal = ()  # Only include this if needed for many-to-many fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

User = get_user_model()
admin.site.register(User, UserAdmin)

# admin.site.unregister(Group)  # Only do this if you want to remove Groups from admin
