from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from sales.views import (
    StartConversationView, ConversationListView, ConversationDetailView,
    SendMessageView, ConversationMessagesJSONView, AdConversationListView,
    UpdateMessageView, DeleteMessageView
)

urlpatterns = [
    path('', include('sales.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path('ads/<int:ad_id>/message/', StartConversationView.as_view(), name='start_conversation'),
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/<int:conversation_id>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/<int:conversation_id>/send/', SendMessageView.as_view(), name='send_message'),
    path('conversations/<int:conversation_id>/messages_json/', ConversationMessagesJSONView.as_view(), name='conversation_messages_json'),
    path('ads/<int:ad_id>/conversations/', AdConversationListView.as_view(), name='conversation_list_for_ad'),
    path('messages/<int:message_id>/update/', UpdateMessageView.as_view(), name='update_message'),
    path('messages/<int:message_id>/delete/', DeleteMessageView.as_view(), name='delete_message'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
