import datetime

from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy, reverse

from blog.constants import num_of_posts
from blog.forms import CreatePostForm, CommentsForm
from blog.models import Category, Comments, Post, User
from blog.service import paginator, get_post_list


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)

    post_list = get_post_list().filter(
        category__slug=category_slug,
        category__is_published=True,
        is_published=True,
        pub_date__lte=datetime.datetime.now()
    ).order_by('-pub_date')

    context = {
        'page_obj': paginator(post_list, num_of_posts, request),
        'category': category
    }
    return render(request, 'blog/category.html', context)


# Профиль.
class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        post_list = get_post_list()

        if self.request.user == user:
            post_list = post_list.filter(
                author__username=user
            ).order_by('-pub_date').annotate(comment_count=Count("comments"))
        else:
            post_list = post_list.filter(
                is_published=True,
                pub_date__lte=datetime.datetime.now()
            ).order_by('-pub_date').annotate(comment_count=Count("comments"))

        context = {
            'profile': user,
            'page_obj': paginator(post_list, num_of_posts, self.request)
        }
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
        return reverse(
            'blog:profile', kwargs={"username": self.request.user}
        )


# Посты.
class PostMixin:
    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'

    def get_queryset(self):
        post_list = get_post_list().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.datetime.now()
        ).order_by('-pub_date').annotate(comment_count=Count("comments"))
        return post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            'page_obj': paginator(
                self.get_queryset(),
                num_of_posts,
                self.request)
        }

        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        return super(PostDetailView, self).get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.get_object().author == self.request.user:
            context['page_obj'] = get_object_or_404(
                Post.objects.all().filter(
                    Q(is_published=True) | (Q(
                        is_published=False) & Q(
                            author=self.request.user))),
                pk=self.kwargs.get('pk'))
        else:
            context['page_obj'] = get_object_or_404(
                get_post_list().filter(
                    is_published=True,
                    category__is_published=True,
                    pub_date__lte=datetime.datetime.now()),
                pk=self.kwargs.get('pk'))

        context['form'] = CommentsForm()
        context['comments'] = (
            self.object.comments.select_related('author')
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
        return reverse(
            'blog:profile',
            kwargs={"username": self.request.user}
        )


class EditPostUpdateView(PostMixin, LoginRequiredMixin, UpdateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class DeletePostDeleteView(PostMixin, LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


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
    comment = get_object_or_404(Comments, pk=comment_id, post__id=post_id)
    form = CommentsForm(request.POST or None, instance=comment)

    if form.is_valid() and comment.author == request.user:
        comment.save()
        return redirect('blog:post_detail', pk=post_id)

    return render(
        request,
        'blog/comment.html',
        context={
            'comment': comment,
            'form': form
        }
    )


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comments, id=comment_id, post__id=post_id)

    if request.method == 'POST' and instance.author == request.user:
        instance.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html')
