from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Compra, ItemCompra
from carrinho.models import Carrinho

@login_required
def finalizar_compra(request):
    carrinho = Carrinho.objects.filter(user=request.user).first()

    if not carrinho or carrinho.itens.count() == 0:
        return redirect('catalogo:listar_livros')

    if request.method == 'POST':
        endereco = request.POST.get('endereco')
        compra = Compra.objects.create(user=request.user, endereco=endereco)

        for item in carrinho.itens.all():
            ItemCompra.objects.create(compra=compra,livro=item.livro, quantidade=item.quantidade)
            
        carrinho.itens.all().delete()

        return redirect('compras:historico')

    return render(request, 'compras/finalizar_compra.html', {'carrinho': carrinho})

@login_required
def historico_compras(request):
    compras = Compra.objects.filter(user=request.user).order_by('-data')

    return render(request, 'compras/historico_compras.html', {'compras': compras})
# Create your views here.
