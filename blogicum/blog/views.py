from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post, Category, User, Comments
from blog.forms import CreatePostForm, CommentsForm

import datetime

from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q


def category_posts(request, category_slug):
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)
    post_list = category.posts.filter(
        is_published=True,
        pub_date__lte=datetime.datetime.now()).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category': category
    }
    return render(request, 'blog/category.html', context)


# Профиль.
class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        post_list = Post.objects.select_related(
            'category',
            'author',
            'location').filter(author__username=user).order_by('-pub_date')

        paginator = Paginator(post_list, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'profile': user,
                   'page_obj': page_obj}
        return context


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'username', 'email')

    def get_object(self):
        return get_object_or_404(User, username=self.request.user)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={"username": self.request.user}
        )


# Посты.
class IndexListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        post_list = Post.objects.select_related(
            'category',
            'author',
            'location').filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=datetime.datetime.now()).order_by('-pub_date')

        paginator = Paginator(post_list, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'page_obj': page_obj}

        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        if post.author == self.request.user:
            context['page_obj'] = get_object_or_404(
                Post.objects.all().filter(
                    Q(is_published=True) | (Q(
                        is_published=False) & Q(
                            author=self.request.user))),
                pk=self.kwargs.get('pk'))
        else:
            context['page_obj'] = get_object_or_404(
                Post.objects.select_related(
                    'category',
                    'author',
                    'location').filter(
                        is_published=True, category__is_published=True,
                        pub_date__lte=datetime.datetime.now()),
                pk=self.kwargs.get('pk'))

        context['form'] = CommentsForm()
        context['comments'] = (
            self.object.comment.select_related('post')
        )
        return context


class CreatePostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={"username": self.request.user})


class EditPostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)


class DeletePostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)


# Комменты.
@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentsForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comments, id=comment_id, post__id=post_id)
    instance = get_object_or_404(Comments, pk=comment_id)
    form = CommentsForm(request.POST or None, instance=instance)
    context = {
        'comment': comment,
        'form': form
    }

    if form.is_valid() and instance.author == request.user:
        instance = form.save(commit=False)
        instance.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comments, id=comment_id, post__id=post_id)
    instance = get_object_or_404(Comments, pk=comment_id)
    context = {
        'comment': comment,
    }

    if request.method == 'POST' and instance.author == request.user:
        instance.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)
