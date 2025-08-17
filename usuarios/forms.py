from tkinter import Widget
from django import forms
from .models import CustomUser, Perfil

class CadastroForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput)
    endereco = forms.CharField(widget=forms.TextInput)

class Meta:
    model = CustomUser
    fields = ['email']

nome = forms.CharField(max_length=255)

def save(self, commit=True):
    email = self.cleaned_data['email']
    senha = self.cleaned_data['senha']
    nome = self.cleaned_data['nome']
    endereco = self.cleaned_data['endereco']
    
    user = CustomUser(email=email)
    user.set_password(senha)
    
    if commit:
        user.save()
        perfil = Perfil(user=user, nome=nome, endereco=endereco)
        perfil.save()
    return user

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)