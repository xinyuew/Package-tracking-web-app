from django import forms

from models import *


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=200,
                               widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "Username"}))

    first_name = forms.CharField(max_length=200,
                                 widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "First name"}))

    last_name = forms.CharField(max_length=200,
                                widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "Last name"}))

    email = forms.EmailField(max_length=200,
                             widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "Email address"}))

    password1 = forms.CharField(max_length=200,
                                label='Password',
                                widget=forms.PasswordInput(attrs={'class': "form-control", 'placeholder': "Password"}))
    password2 = forms.CharField(max_length=200,
                                label='Confirm password',
                                widget=forms.PasswordInput(
                                    attrs={'class': "form-control", 'placeholder': "Confirm password"}))

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        return username


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'followers', 'tracks', 'roommates')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': "form-control", 'placeholder': 'Email'}),
            'age': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Age'}),
            'location': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Location'}),
            'bio': forms.Textarea(attrs={'class': "form-control bio", 'placeholder': 'Bio'}),
            'picture': forms.FileInput(attrs={'class': "form-group"}),
        }

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        return cleaned_data


class RoommateForm(forms.Form):
    username = forms.CharField(max_length=200, required=False, label="",
                               widget=forms.TextInput(
                                   attrs={'class': "form-control", 'placeholder': "Username", 'style': 'height:40px'}))

    def clean(self):
        cleaned_data = super(RoommateForm, self).clean()
        username = cleaned_data.get('username')

        if not User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username doesn't exist, please enter a validate username!")

        return cleaned_data
