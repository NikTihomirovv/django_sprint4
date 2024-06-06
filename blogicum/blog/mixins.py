from blog.models import Post
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy


class PostMixin:

    def get_object(self):
        return get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)


class DeleteAndEditPostMixin:
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'pk'
