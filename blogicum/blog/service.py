from django.core.paginator import Paginator
from blog.models import Post


def paginator(post_list, num_of_posts, request):
    return Paginator(
        post_list,
        num_of_posts
    ).get_page(request.GET.get('page'))


def get_post_list():
    return Post.objects.select_related(
        'category',
        'author',
        'location'
    )
