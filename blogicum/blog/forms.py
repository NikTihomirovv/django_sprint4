from django import forms
from .models import Post, User, Comments
from .models import User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)
        author = forms.CharField(required=True)
