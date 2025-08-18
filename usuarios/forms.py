from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Perfil, Endereco

User = get_user_model()

class CadastroForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='Nome', required=True)
    last_name = forms.CharField(max_length=30, label='Sobrenome', required=True)
    
   
    nome_endereco = forms.CharField(max_length=100, label='Nome do Endereço', 
                                   help_text="Ex: Casa, Trabalho, etc.")
    cep = forms.CharField(max_length=9, label='CEP')
    rua = forms.CharField(max_length=200, label='Rua')
    numero = forms.CharField(max_length=10, label='Número')
    complemento = forms.CharField(max_length=100, label='Complemento', required=False)
    bairro = forms.CharField(max_length=100, label='Bairro')
    cidade = forms.CharField(max_length=100, label='Cidade')
    estado = forms.CharField(max_length=2, label='Estado')
    
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
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.set_password(self.cleaned_data['senha1'])
        
        if commit:
            user.save()
            
            Perfil.objects.create(user=user, nome=f"{user.first_name} {user.last_name}")
            
            Endereco.objects.create(
                user=user,
                nome_endereco=self.cleaned_data['nome_endereco'],
                cep=self.cleaned_data['cep'],
                rua=self.cleaned_data['rua'],
                numero=self.cleaned_data['numero'],
                complemento=self.cleaned_data['complemento'],
                bairro=self.cleaned_data['bairro'],
                cidade=self.cleaned_data['cidade'],
                estado=self.cleaned_data['estado']
            )
        
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(label='E-mail')
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['nome_endereco', 'cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado']
        labels = {
            'nome_endereco': 'Nome do Endereço',
            'cep': 'CEP',
            'rua': 'Rua',
            'numero': 'Número',
            'complemento': 'Complemento',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'estado': 'Estado'
        }
