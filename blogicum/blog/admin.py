from django.contrib import admin

from .models import Category, Comments, Location, Post


class PostAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'text',
        'pub_date',
    )

    list_editable = (
        'pub_date',
    )

    search_fields = ('title',)
    list_filter = ('pub_date',)
    list_display_links = ('title',)


class CommentsAdmin(admin.ModelAdmin):

    list_display = (
        'post',
        'text',
        'author',
    )

    list_editable = (
        'text',
    )

    search_fields = ('post', 'author',)
    list_filter = ('post',)
    list_display_links = ('post',)


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
admin.site.register(Comments, CommentsAdmin)
