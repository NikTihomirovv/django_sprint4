from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Посты.
    path('',
         views.IndexListView.as_view(),
         name='index'),

    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'),

    path('posts/create/',
         views.CreatePostCreateView.as_view(),
         name='create_post'),

    path('posts/<int:pk>/edit/',
         views.EditPostUpdateView.as_view(),
         name='edit_post'),

    path('posts/<int:pk>/delete/',
         views.DeletePostDeleteView.as_view(),
         name='delete_post'),

    # Комменты.
    path('posts/<int:pk>/comment/',
         views.add_comment,
         name='add_comment'),

    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment,
         name='edit_comment'),

    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.delete_comment,
         name='delete_comment'),




    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),

    # Профиль.
    path('profile/<slug:username>/',
         views.ProfileListView.as_view(),
         name='profile'),

    path('edit_profile/',
         views.EditProfileUpdateView.as_view(),
         name='edit_profile'),
]
