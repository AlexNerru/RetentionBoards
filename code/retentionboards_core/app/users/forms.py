from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), label='Password', max_length=100)


class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), label='Password', max_length=100)
    password2 = forms.CharField(widget=forms.PasswordInput(), label='Password', max_length=100)
