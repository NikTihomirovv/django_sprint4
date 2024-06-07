from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.constants import PAGINATE_BY
from blog.forms import CommentsForm, CreatePostForm
from blog.models import Category, Comments, Post, User
from blog.service import (filter_post_list, get_post_list,
                          order_and_annotate_post_list, paginator)

from .mixins import DeleteAndEditPostMixin, PostMixin


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)

    post_list = filter_post_list(get_post_list()).filter(
        category__slug=category_slug
    ).order_by('-pub_date')

    context = {
        'page_obj': paginator(post_list, PAGINATE_BY, request),
        'category': category
    }
    return render(request, 'blog/category.html', context)


# Профиль.
class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        post_list = order_and_annotate_post_list(get_post_list().filter(author=user))

        if self.request.user != user:
            post_list = filter_post_list(post_list)

        context = {
            'profile': user,
            'page_obj': paginator(post_list, PAGINATE_BY, self.request)
        }
        return context


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'username', 'email')

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={"username": self.request.user}
        )


# Посты.
class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        post_list = order_and_annotate_post_list(filter_post_list(get_post_list()))
        return post_list


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, post=Post):
        return get_object_or_404(post, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.get_object().author != self.request.user:
            post_list = filter_post_list(get_post_list())
            context['post'] = self.get_object(post_list)

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


class EditPostUpdateView(
    LoginRequiredMixin,
    DeleteAndEditPostMixin,
    PostMixin,
    UpdateView
):
    form_class = CreatePostForm


class DeletePostDeleteView(
    LoginRequiredMixin,
    DeleteAndEditPostMixin,
    PostMixin,
    DeleteView
):
    pass


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
