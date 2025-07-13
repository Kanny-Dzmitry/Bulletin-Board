from django.urls import path
from . import views

app_name = 'bulletin_board'

urlpatterns = [
    # Главная страница
    path('', views.PostListView.as_view(), name='post_list'),
    
    # Категории
    path('category/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Объявления
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # Отклики
    path('post/<int:post_pk>/response/', views.ResponseCreateView.as_view(), name='response_create'),
    path('response/<int:pk>/accept/', views.ResponseAcceptView.as_view(), name='response_accept'),
    path('response/<int:pk>/reject/', views.ResponseRejectView.as_view(), name='response_reject'),
    path('response/<int:pk>/delete/', views.ResponseDeleteView.as_view(), name='response_delete'),
    
    # Пользовательские страницы
    path('my-posts/', views.MyPostsView.as_view(), name='my_posts'),
    path('my-responses/', views.MyResponsesView.as_view(), name='my_responses'),
    path('responses-to-posts/', views.ResponsesToPostsView.as_view(), name='responses_to_posts'),
    
    # Поиск
    path('search/', views.SearchView.as_view(), name='search'),
    
    # API endpoints для AJAX
    path('api/post/<int:pk>/toggle-status/', views.toggle_post_status, name='toggle_post_status'),
    path('api/response/<int:pk>/toggle-status/', views.toggle_response_status, name='toggle_response_status'),
] 