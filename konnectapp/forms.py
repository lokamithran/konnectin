import datetime

from django import forms
from django.forms import ModelForm
from .models import Question


class PostForm(forms.ModelForm):




    class Meta:
        model = Question
        fields = ['question_title', 'date_created', 'tags']
