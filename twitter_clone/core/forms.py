from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Tweet, Comment, Message

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'profile_pic']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TweetForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': "What's happening?",
            'class': 'form-control border-0 shadow-none',
            'style': 'resize: none; font-size: 1.1rem;'
        }),
        max_length=280
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'd-none',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Tweet
        fields = ['content', 'image']


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': "Write a comment...",
            'class': 'form-control border-0 shadow-none',
            'style': 'resize: none; min-height: 60px;'
        }),
        max_length=280
    )

    class Meta:
        model = Comment
        fields = ['content']


class MessageForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': "Type your message...",
            'class': 'form-control rounded-pill py-2 px-3',
            'style': 'resize: none; min-height: 60px;'
        }),
        max_length=1000
    )

    class Meta:
        model = Message
        fields = ['content']
