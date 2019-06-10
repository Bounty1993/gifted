from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset

from .models import Post, Thread


class PostCreateForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            {'col': 5}
        ),
        help_text='Tutaj napisz swój komentarz. Maksymalnie 500 znaków',
        label='Treść'
    )

    class Meta:
        model = Post
        fields = [
            'subject',
            'content',
        ]


class ThreadCreateForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = [
            'author',
            'post',
            'subject',
            'content',
        ]


class PostUpdateForm(PostCreateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Zapisz'))