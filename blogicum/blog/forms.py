from django import forms
from .models import Post, Comments


class CreatePostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        fields = ('title', 'text', 'category', 'location', 'pub_date', 'image')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentsForm(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ('text',)
