from django.shortcuts import render, get_object_or_404
from .models import Livro, Autor, Categoria

def listar_livros(request):
    categoria = request.GET.get('categoria')
    titulo = request.GET.get('titulo')
    autor = request.GET.get('autor')

    livros = Livro.objects.all()

    if categoria:
        livros = livros.filter(categoria__nome__icontains=categoria)
    if titulo:
        livros = livros.filter(titulo__icontains=titulo)
    if autor:
        livros = livros.filter(autor__nome__icontains=autor)

    context = {
        'livros': livros
    }
    return render(request, 'catalogo/listar_livros.html', context)

def detalhes_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    return render(request, 'catalogo/detalhes_livro.html', {'livro': livro})
    
