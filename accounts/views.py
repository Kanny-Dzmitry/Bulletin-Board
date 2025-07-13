from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, UpdateView, DetailView
from django.db.models import Count
from .models import UserProfile
from .forms import UserProfileForm, UserUpdateForm
from bulletin_board.models import Post, Response

# Create your views here.

class DashboardView(LoginRequiredMixin, TemplateView):
    """Панель управления пользователя"""
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Статистика пользователя
        context['posts_count'] = Post.objects.filter(author=user).count()
        context['active_posts_count'] = Post.objects.filter(author=user, status='active').count()
        context['responses_count'] = Response.objects.filter(author=user).count()
        context['responses_to_posts_count'] = Response.objects.filter(post__author=user).count()
        context['unread_notifications'] = user.notifications.filter(is_read=False).count()
        
        # Последние объявления
        context['recent_posts'] = Post.objects.filter(author=user).order_by('-created_at')[:5]
        
        # Последние отклики
        context['recent_responses'] = Response.objects.filter(author=user).select_related('post').order_by('-created_at')[:5]
        
        # Отклики на объявления пользователя
        context['recent_responses_to_posts'] = Response.objects.filter(
            post__author=user
        ).select_related('author', 'post').order_by('-created_at')[:5]
        
        return context


class ProfileView(LoginRequiredMixin, DetailView):
    """Просмотр собственного профиля"""
    model = UserProfile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'
    
    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Статистика пользователя
        context['posts_count'] = Post.objects.filter(author=user).count()
        context['responses_count'] = Response.objects.filter(author=user).count()
        context['joined_date'] = user.date_joined
        
        # Последние активности
        context['recent_posts'] = Post.objects.filter(author=user).order_by('-created_at')[:3]
        
        return context


class PublicProfileView(DetailView):
    """Публичный профиль пользователя"""
    model = UserProfile
    template_name = 'accounts/public_profile.html'
    context_object_name = 'profile'
    
    def get_object(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        return get_object_or_404(UserProfile, user=user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object.user
        
        # Статистика пользователя
        context['posts_count'] = Post.objects.filter(author=user, status='active').count()
        context['responses_count'] = Response.objects.filter(author=user).count()
        context['joined_date'] = user.date_joined
        
        # Публичные объявления
        context['recent_posts'] = Post.objects.filter(
            author=user, 
            status='active'
        ).order_by('-created_at')[:5]
        
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        
        if user_form.is_valid():
            user_form.save()
            messages.success(self.request, 'Профиль успешно обновлен!')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class SettingsView(LoginRequiredMixin, TemplateView):
    """Настройки пользователя"""
    template_name = 'accounts/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        return context
    
    def post(self, request, *args, **kwargs):
        """Обработка изменения настроек"""
        profile = request.user.profile
        
        # Обновляем настройки уведомлений
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.newsletter_subscription = request.POST.get('newsletter_subscription') == 'on'
        profile.save()
        
        messages.success(request, 'Настройки успешно сохранены!')
        return redirect('accounts:settings')


class PasswordChangeView(LoginRequiredMixin, DjangoPasswordChangeView):
    """Смена пароля"""
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Пароль успешно изменен!')
        return super().form_valid(form)


# Функциональные представления

@login_required
def delete_account(request):
    """Удаление аккаунта"""
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()
        messages.success(request, 'Аккаунт успешно деактивирован!')
        return redirect('account_logout')
    
    return render(request, 'accounts/delete_account.html')
