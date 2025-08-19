from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Livro, Autor, Categoria
import requests
from datetime import datetime

def _ol_fetch_details(work_key: str, edition_keys: list[str]):
    sinopse = ""
    paginas = None
    # Detalhes do work
    try:
        r = requests.get(f"https://openlibrary.org/works/{work_key}.json", timeout=6)
        if r.status_code == 200:
            data = r.json()
            desc = data.get("description")
            if desc:
                if isinstance(desc, dict):
                    sinopse = desc.get("value") or ""
                elif isinstance(desc, str):
                    sinopse = desc
            # Algumas vezes vem aqui também
            paginas = paginas or data.get("number_of_pages_median") or data.get("number_of_pages")
    except:
        pass
    # Se ainda não tem páginas, tentar por edição
    if not paginas and edition_keys:
        ek = edition_keys[0]
        try:
            r2 = requests.get(f"https://openlibrary.org/books/{ek}.json", timeout=6)
            if r2.status_code == 200:
                data2 = r2.json()
                paginas = data2.get("number_of_pages")
        except:
            pass
    return sinopse, paginas

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

    if titulo or autor or categoria:
        try:
            params = {}
            if titulo:
                params['title'] = titulo
            if autor:
                params['author'] = autor
            if categoria:
                params['subject'] = categoria

            resp = requests.get("https://openlibrary.org/search.json", params=params, timeout=10)
            resp.raise_for_status()
            payload = resp.json()

            for doc in payload.get('docs', [])[:10]:
                # key costuma vir como "/works/OLxxxxW" → normalizar p/ "OLxxxxW"
                raw_key = doc.get('key') or ""
                work_key = raw_key.split('/')[-1] if raw_key else None
                if not work_key:
                    continue

                # evitar duplicata: comparar armazenado normalizado
                if Livro.objects.filter(externo_ID__in=[work_key, raw_key]).exists():
                    continue

                autor_nome = ", ".join(doc.get('author_name', [])) if doc.get('author_name') else 'Autor não informado'
                autor_obj, _ = Autor.objects.get_or_create(nome=autor_nome)

                categoria_nome = ", ".join(doc.get('subject', [])[:3]) if doc.get('subject') else 'Categoria não informada'
                categoria_obj, _ = Categoria.objects.get_or_create(nome=categoria_nome)

                # Data de publicação (fallback: 01/01/ano ou hoje)
                if doc.get('first_publish_year'):
                    try:
                        data_pub = datetime(int(doc['first_publish_year']), 1, 1).date()
                    except:
                        data_pub = datetime.now().date()
                else:
                    data_pub = datetime.now().date()

                # Buscar sinopse e páginas nos endpoints de detalhes
                edition_keys = doc.get('edition_key', []) or []
                sinopse, paginas = _ol_fetch_details(work_key, edition_keys)

                # Fallback para sinopse a partir da busca (first_sentence pode vir em vários formatos)
                if not sinopse:
                    fs = doc.get('first_sentence')
                    if isinstance(fs, list):
                        sinopse = fs[0] if fs else ''
                    elif isinstance(fs, dict):
                        sinopse = fs.get('value') or ''
                    elif isinstance(fs, str):
                        sinopse = fs

                capa = f"https://covers.openlibrary.org/b/id/{doc.get('cover_i')}-M.jpg" if doc.get('cover_i') else ''
                publicadora = ", ".join(doc.get('publisher', [])) if doc.get('publisher') else 'Editora não informada'

                livro_novo = Livro.objects.create(
                    titulo=doc.get('title', 'Título não disponível'),
                    autor=autor_obj,
                    categoria=categoria_obj,
                    data_publicacao=data_pub,
                    capa=capa,
                    publicadora=publicadora,
                    sinopse=sinopse or '',
                    numero_paginas=paginas,
                    externo_ID=work_key,  # guardar normalizado
                )
                livros = livros | Livro.objects.filter(id=livro_novo.id)
        except requests.RequestException:
            pass

    livros = livros.order_by('titulo')

    paginator = Paginator(livros, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'livros': page_obj,
        'tem_busca': bool(titulo or autor or categoria),
        'titulo_busca': titulo,
        'autor_busca': autor,
        'categoria_busca': categoria,
    }
    return render(request, 'catalogo/listar_livros.html', context)

def detalhes_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    # Se veio da OL e ainda falta dado, tentar completar on-demand
    if livro.externo_ID and (not livro.sinopse or not livro.numero_paginas):
        sinopse, paginas = _ol_fetch_details(livro.externo_ID, [])
        if sinopse and not livro.sinopse:
            livro.sinopse = sinopse
        if paginas and not livro.numero_paginas:
            livro.numero_paginas = paginas
        livro.save()
    return render(request, 'catalogo/detalhes_livro.html', {'livro': livro})