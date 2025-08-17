from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Perfil

User = get_user_model()

class CadastroForm(forms.ModelForm):
    nome = forms.CharField(max_length=255, label='Nome')
    endereco = forms.CharField(max_length=255, label='Endereço')
    senha1 = forms.CharField(widget=forms.PasswordInput, label='Senha')
    senha2 = forms.CharField(widget=forms.PasswordInput, label='Confirmar Senha')

    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Já existe um usuário com esse e-mail.')
        return email

    def clean_senha2(self):
        senha1 = self.cleaned_data.get('senha1')
        senha2 = self.cleaned_data.get('senha2')
        
        if senha1 and senha2:
            if senha1 != senha2:
                raise forms.ValidationError('As senhas não coincidem.')
            if len(senha1) < 8:
                raise forms.ValidationError('A senha deve ter pelo menos 8 caracteres.')
        
        return senha2

    @transaction.atomic
    def save(self, commit=True):
        email = self.cleaned_data['email']
        senha = self.cleaned_data['senha1']  # Mudou de 'senha' para 'senha1'
        nome = self.cleaned_data['nome']
        endereco = self.cleaned_data['endereco']

        user = User.objects.create_user(email=email, password=senha)
        Perfil.objects.create(user=user, nome=nome, endereco=endereco)

        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='E-mail')
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')
