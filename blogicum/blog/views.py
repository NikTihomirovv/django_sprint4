import pdb
from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post, Category, User, Comments
import datetime
from .forms import PostForm, CommentsForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.generic import (DetailView,
                                  ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView,
                                  )
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


# Pages.
class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    odrdering = 'id'
    paginate_by = '10'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        context['page_obj'] = Post.objects.select_related(
            'category',
            'author',
            'location').filter(
                pub_date__lte=datetime.datetime.now(),
                is_published=True,
                category__is_published=True)

        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        context['comments'] = Comments.objects.select_related('post').filter(
            post__id=self.object.pk)

        return context


def category_posts(request, category_slug):
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)
    post_list = category.posts.filter(
        is_published=True,
        pub_date__lte=datetime.datetime.now())

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category': category
    }
    return render(request, 'blog/category.html', context)


# Posts.
class PostMixin:
    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={"username": self.request.user}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView, PostMixin):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'blog/create.html'
    model = Post
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


# Profile.
class ProfileCreateView(CreateView):
    pdb.set_trace()
    model = User
    template_name = 'blog/profile.html'
    fields = '__all__'
    success_url = reverse_lazy('blog:create')

    def get_full_name(self, **kwargs):
        full_name = str(self.first_name) + ' ' + str(self.last_name)
        return full_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = get_object_or_404(User, username=self.kwargs.get('username'))
        post_list = Post.objects.select_related(
            'category',
            'author',
            'location').filter(is_published=True, author__username=user)

        paginator = Paginator(post_list, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'profile': user,
                   'page_obj': page_obj}

        return context


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = '__all__'
#    success_url = reverse_lazy('blog:edit')

    def get_object(self):
        return get_object_or_404(User, username=self.request.user)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={"username": self.request.user}
        )


# Comments.
@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentsForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

#       instance = form.save(commit=False)
#       instance.author = request.user
#       instance.save()

    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, pk, comment_id):
    comment = get_object_or_404(Comments, id=comment_id, post__id=pk)
    instance = get_object_or_404(Comments, pk=comment_id)
    form = CommentsForm(request.POST or None, instance=instance)

    context = {
        'comment': comment,
        'form': form
    }

    if form.is_valid():
        comment = form.save(commit=True)
        return redirect('blog:post_detail', pk=pk)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, pk, comment_id):
    comment = get_object_or_404(Comments, id=comment_id, post__id=pk)
    instance = get_object_or_404(Comments, pk=comment_id)
    form = CommentsForm(request.POST or None, instance=instance)
    context = {
        'comment': comment,
        'form': form
    }

    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk=pk)
    return render(request, 'blog/comment.html', context)
