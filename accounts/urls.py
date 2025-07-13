from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Профиль пользователя
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/<int:pk>/', views.PublicProfileView.as_view(), name='public_profile'),
    
    # Настройки
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('settings/password/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # Дополнительные страницы
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
] 