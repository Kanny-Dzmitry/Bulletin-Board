from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Список уведомлений
    path('', views.NotificationListView.as_view(), name='notification_list'),
    
    # Детальный просмотр уведомления
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    
    # Действия с уведомлениями
    path('<int:pk>/mark-read/', views.MarkReadView.as_view(), name='mark_read'),
    path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark_all_read'),
    path('<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='notification_delete'),
    
    # API endpoints для AJAX
    path('api/count/', views.unread_count, name='unread_count'),
    path('api/<int:pk>/mark-read/', views.mark_read_ajax, name='mark_read_ajax'),
    path('api/mark-all-read/', views.mark_all_read_ajax, name='mark_all_read_ajax'),
] 