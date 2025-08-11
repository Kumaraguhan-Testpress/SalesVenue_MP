from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Ad, Message, AdImage, Conversation
from ordered_model.admin import OrderedTabularInline


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'phone_number']
    fieldsets = UserAdmin.fieldsets + (
        ('Contact Information', {'fields': ('phone_number', 'contact_info_visibility')}),
        ('Profile', {'fields': ('profile_picture',)}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


class AdImageInline(OrderedTabularInline):
    model = AdImage
    extra = 1
    ordering = ('order',)

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'location']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user', 'category']
    inlines = [AdImageInline]

@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    list_display = ('ad', 'image', 'order')
    list_filter = ('ad',)
    search_fields = ('ad__title',)
    raw_id_fields = ('ad',)
    ordering = ('ad', 'order')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['ad_title', 'sender', 'recipient', 'sent_at', 'read']
    list_filter = ['read', 'sent_at']
    search_fields = ['content', 'conversation__ad__title', 'sender__username', 'sender__email']
    date_hierarchy = 'sent_at'
    raw_id_fields = ['conversation', 'sender']

    def ad_title(self, obj):
        return obj.conversation.ad.title
    ad_title.short_description = 'Ad'

    def recipient(self, obj):
        return obj.conversation.other_user(obj.sender)
    recipient.short_description = 'Recipient'

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['ad', 'owner', 'buyer', 'created_at']
    search_fields = ['ad__title', 'owner__username', 'buyer__username']
    raw_id_fields = ['ad', 'owner', 'buyer']
