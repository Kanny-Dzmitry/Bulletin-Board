from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Post, Category, Response, Newsletter
from .forms import PostForm, ResponseForm, SearchForm

# Create your views here.

class PostListView(ListView):
    """Главная страница со списком объявлений"""
    model = Post
    template_name = 'bulletin_board/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Post.objects.filter(status='active').select_related('author', 'category')
        
        # Фильтрация по категории
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Поиск
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_form'] = SearchForm(self.request.GET)
        context['current_category'] = self.request.GET.get('category')
        return context


class CategoryDetailView(DetailView):
    """Страница категории с объявлениями"""
    model = Category
    template_name = 'bulletin_board/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(
            category=self.object,
            status='active'
        ).select_related('author').order_by('-created_at')
        
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['posts'] = paginator.get_page(page_number)
        return context


class PostDetailView(DetailView):
    """Детальная страница объявления"""
    model = Post
    template_name = 'bulletin_board/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.select_related('author', 'category').prefetch_related('responses')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Отклики на объявление
        responses = self.object.responses.filter(status='pending').select_related('author')
        context['responses'] = responses
        context['responses_count'] = responses.count()
        
        # Форма для отклика
        if self.request.user.is_authenticated and self.request.user != self.object.author:
            context['response_form'] = ResponseForm()
        
        # Проверяем, оставлял ли пользователь отклик
        if self.request.user.is_authenticated:
            context['user_response'] = self.object.responses.filter(
                author=self.request.user
            ).first()
        
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового объявления"""
    model = Post
    form_class = PostForm
    template_name = 'bulletin_board/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Объявление успешно создано!')
        return response
    
    def get_success_url(self):
        return reverse('bulletin_board:post_detail', kwargs={'pk': self.object.pk})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование объявления"""
    model = Post
    form_class = PostForm
    template_name = 'bulletin_board/post_form.html'
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Объявление успешно обновлено!')
        return response
    
    def get_success_url(self):
        return reverse('bulletin_board:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление объявления"""
    model = Post
    template_name = 'bulletin_board/post_confirm_delete.html'
    success_url = reverse_lazy('bulletin_board:my_posts')
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Объявление успешно удалено!')
        return super().delete(request, *args, **kwargs)


class ResponseCreateView(LoginRequiredMixin, CreateView):
    """Создание отклика на объявление"""
    model = Response
    form_class = ResponseForm
    template_name = 'bulletin_board/response_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=kwargs['post_pk'])
        
        # Проверяем, что пользователь не автор объявления
        if request.user == self.post.author:
            messages.error(request, 'Вы не можете оставить отклик на свое объявление!')
            return redirect('bulletin_board:post_detail', pk=self.post.pk)
        
        # Проверяем, что пользователь еще не оставлял отклик
        if Response.objects.filter(post=self.post, author=request.user).exists():
            messages.error(request, 'Вы уже оставили отклик на это объявление!')
            return redirect('bulletin_board:post_detail', pk=self.post.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.post = self.post
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Отклик успешно отправлен!')
        return response
    
    def get_success_url(self):
        return reverse('bulletin_board:post_detail', kwargs={'pk': self.post.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post
        return context


class ResponseAcceptView(LoginRequiredMixin, DetailView):
    """Принятие отклика"""
    model = Response
    
    def get_queryset(self):
        return Response.objects.filter(post__author=self.request.user)
    
    def post(self, request, *args, **kwargs):
        response = self.get_object()
        response.status = 'accepted'
        response.save()
        messages.success(request, 'Отклик принят!')
        return redirect('bulletin_board:responses_to_posts')


class ResponseRejectView(LoginRequiredMixin, DetailView):
    """Отклонение отклика"""
    model = Response
    
    def get_queryset(self):
        return Response.objects.filter(post__author=self.request.user)
    
    def post(self, request, *args, **kwargs):
        response = self.get_object()
        response.status = 'rejected'
        response.save()
        messages.success(request, 'Отклик отклонен!')
        return redirect('bulletin_board:responses_to_posts')


class ResponseDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление отклика"""
    model = Response
    template_name = 'bulletin_board/response_confirm_delete.html'
    success_url = reverse_lazy('bulletin_board:my_responses')
    
    def get_queryset(self):
        return Response.objects.filter(
            Q(author=self.request.user) | Q(post__author=self.request.user)
        )
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Отклик успешно удален!')
        return super().delete(request, *args, **kwargs)


class MyPostsView(LoginRequiredMixin, ListView):
    """Мои объявления"""
    model = Post
    template_name = 'bulletin_board/my_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).select_related('category').order_by('-created_at')


class MyResponsesView(LoginRequiredMixin, ListView):
    """Мои отклики"""
    model = Response
    template_name = 'bulletin_board/my_responses.html'
    context_object_name = 'responses'
    paginate_by = 10
    
    def get_queryset(self):
        return Response.objects.filter(author=self.request.user).select_related('post', 'post__author').order_by('-created_at')


class ResponsesToPostsView(LoginRequiredMixin, ListView):
    """Отклики на мои объявления"""
    model = Response
    template_name = 'bulletin_board/responses_to_posts.html'
    context_object_name = 'responses'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Response.objects.filter(
            post__author=self.request.user
        ).select_related('author', 'post')
        
        # Фильтрация по объявлению
        post_id = self.request.GET.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        # Фильтрация по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_posts'] = Post.objects.filter(author=self.request.user).values('id', 'title')
        context['current_post'] = self.request.GET.get('post')
        context['current_status'] = self.request.GET.get('status')
        return context


class SearchView(ListView):
    """Поиск объявлений"""
    model = Post
    template_name = 'bulletin_board/search_results.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        form = SearchForm(self.request.GET)
        queryset = Post.objects.filter(status='active').select_related('author', 'category')
        
        if form.is_valid():
            query = form.cleaned_data['q']
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query)
                )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(self.request.GET)
        context['query'] = self.request.GET.get('q', '')
        return context


# API Views для AJAX запросов

@login_required
@require_POST
@csrf_exempt
def toggle_post_status(request, pk):
    """Переключение статуса объявления"""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if post.status == 'active':
        post.status = 'closed'
    else:
        post.status = 'active'
    
    post.save()
    
    return JsonResponse({
        'success': True,
        'status': post.status,
        'status_display': post.get_status_display()
    })


@login_required
@require_POST
@csrf_exempt
def toggle_response_status(request, pk):
    """Переключение статуса отклика"""
    response = get_object_or_404(Response, pk=pk, post__author=request.user)
    
    if response.status == 'pending':
        new_status = request.POST.get('status', 'accepted')
        response.status = new_status
        response.save()
        
        return JsonResponse({
            'success': True,
            'status': response.status,
            'status_display': response.get_status_display()
        })
    
    return JsonResponse({'success': False, 'error': 'Отклик уже обработан'})
