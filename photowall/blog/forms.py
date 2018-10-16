from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    # Post : Comment = 1:N
    class  Meta:
        model = Comment
        fields = ['message']

