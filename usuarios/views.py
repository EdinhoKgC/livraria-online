from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Perfil, CustomUser
from .forms import CadastroForm, LoginForm

def cadastro(request):
    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('catalogo:listar_livros')
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados.')
    else:
        form = CadastroForm()
    return render(request, 'usuario/cadastro.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data['email'],
                              password=form.cleaned_data['password'])
            if user:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.get_full_name()}!')
                return redirect('catalogo:listar_livros')
            else:
                messages.error(request, 'Email ou senha incorretos.')
    else:
        form = LoginForm()
    return render(request, 'usuario/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('catalogo:listar_livros')

# Create your views here.
