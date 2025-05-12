from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import User, InstructorRequest

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'avatar')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

admin.site.register(User, CustomUserAdmin)

@admin.register(InstructorRequest)
class InstructorRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'user__email')
    actions = ['approve_requests']
    
    def save_model(self, request, obj, form, change):
        if 'is_approved' in form.changed_data and obj.is_approved:
            obj.user.is_staff = True
            obj.user.save(update_fields=['is_staff'])
            messages.success(request, f"کاربر {obj.user.username} به عنوان مدرس تایید شد.")
        super().save_model(request, obj, form, change)

    def approve_requests(self, request, queryset):
        try:
            for instructor_request in queryset:
                instructor_request.is_approved = True
                instructor_request.user.is_staff = True
                instructor_request.user.save(update_fields=['is_staff'])
                instructor_request.save()
            
            self.message_user(request, f"درخواست‌های انتخاب شده با موفقیت تایید شدند.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"خطا در تایید درخواست‌ها: {str(e)}", messages.ERROR)
            
    approve_requests.short_description = "تایید درخواست‌های انتخاب شده"
