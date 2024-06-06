import datetime

from blog.models import Post
from django.core.paginator import Paginator
from django.db.models import Count


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


def filter_post_list(post_list):
    return post_list.filter(
        category__is_published=True,
        is_published=True,
        pub_date__lte=datetime.datetime.now()
    )


def order_and_annotate_post_list(post_list):
    return post_list.order_by(
        '-pub_date'
    ).annotate(
        comment_count=Count("comments")
    )
