from django.shortcuts import render, get_object_or_404, redirect
from .models import Carrinho, ItemCarrinho
from catalogo.models import Livro

def adicionar_ao_carrinho(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)

    if request.user.is_authenticated:
        carrinho, created = Carrinho.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        carrinho, created = Carrinho.objects.get_or_create(session_key=session_key)
    
    item_carrinho, created = ItemCarrinho.objects.get_or_create(carrinho=carrinho,livro=livro)

    if not created:
        item_carrinho.quantidade += 1
        item_carrinho.save()
    return redirect('visualizar_carrinho')

def remover_item(request, livro_id):
    item = get_object_or_404(ItemCarrinho, id=livro_id)
    item.delete()
    return redirect('carrinho:visualizar_carrinho')

def visualizar_carrinho(request):
    if request.user.is_authenticated:
        carrinho = Carrinho.objects.filter(user=request.user).first()

    else:
        session_key = request.session.session_key
        carrinho = Carrinho.objects.filter(session_key=session_key).first()

    itens = carrinho.itens.all() if carrinho else []

    return render(request, 'carrinho/visualizar_carrinho.html',{'itens': itens})
        

