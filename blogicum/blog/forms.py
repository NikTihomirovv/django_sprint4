from django import forms

from .models import Comments, Post


class CreatePostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M:%S',
                attrs={'type': 'datetime-local'})
        }


class CommentsForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 10, 'rows': 3}))

    class Meta:
        model = Comments
        fields = ('text',)
