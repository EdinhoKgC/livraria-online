from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Perfil, CustomUser
from .forms import CadastroForm, LoginForm
from carrinho.models import Carrinho, ItemCarrinho

def _merge_session_cart_into_user(request, user, pre_login_session_key: str | None):
    if not pre_login_session_key:
        return
    carrinho_sessao = Carrinho.objects.filter(session_key=pre_login_session_key).first()
    if not carrinho_sessao:
        return
    carrinho_user, _ = Carrinho.objects.get_or_create(user=user)
    for item in carrinho_sessao.itens.all():
        existente = ItemCarrinho.objects.filter(carrinho=carrinho_user, livro=item.livro).first()
        if existente:
            existente.quantidade += item.quantidade
            existente.save()
        else:
            ItemCarrinho.objects.create(carrinho=carrinho_user, livro=item.livro, quantidade=item.quantidade)
    carrinho_sessao.delete()

def cadastro(request):
    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            # capturar session_key ANTES do login (Django troca a sessão no login)
            pre_session_key = request.session.session_key
            if not pre_session_key:
                request.session.create()
                pre_session_key = request.session.session_key

            user = form.save()
            login(request, user)
            _merge_session_cart_into_user(request, user, pre_session_key)

            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('catalogo:listar_livros')
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados.')
    else:
        form = CadastroForm()
    return render(request, 'usuarios/cadastro.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            # capturar session_key ANTES do login (Django troca a sessão no login)
            pre_session_key = request.session.session_key
            if not pre_session_key:
                request.session.create()
                pre_session_key = request.session.session_key

            user = authenticate(email=form.cleaned_data['email'],
                              password=form.cleaned_data['password'])
            if user:
                login(request, user)
                _merge_session_cart_into_user(request, user, pre_session_key)

                messages.success(request, f'Bem-vindo, {user.get_full_name()}!')
                next_url = request.GET.get('next', 'catalogo:listar_livros')
                return redirect(next_url)
            else:
                messages.error(request, 'Email ou senha incorretos.')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('catalogo:listar_livros')