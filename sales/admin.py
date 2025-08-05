from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Ad, Message, AdImage


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'phone_number']
    fieldsets = UserAdmin.fieldsets + (
        ('Contact Information', {'fields': ('phone_number', 'contact_info_visibility')}),
        ('Profile', {'fields': ('profile_picture',)}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'location']
    date_hierarchy = 'created_at' # Provides a drill-down navigation by date
    raw_id_fields = ['user', 'category'] # Use a searchable input for foreign keys

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['ad', 'sender', 'recipient', 'sent_at', 'read']
    list_filter = ['read', 'sent_at']
    search_fields = ['content']
    date_hierarchy = 'sent_at'
    raw_id_fields = ['sender', 'recipient', 'ad']

@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    list_display = ('ad', 'image', 'order')
    list_filter = ('ad',)
    search_fields = ('ad__title',) # Search by the ad's title
    raw_id_fields = ('ad',) # Use a raw ID field for the ForeignKey to Ad for better performance
    ordering = ('ad', 'order')