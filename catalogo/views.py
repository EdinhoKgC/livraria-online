from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Livro, Autor, Categoria
import requests
from datetime import datetime

def _ol_fetch_details(work_key: str, edition_keys: list[str]):
    """
    Busca detalhes completos de um livro usando vários endpoints da OpenLibrary
    """
    sinopse = ""
    paginas = None
    publicadora = ""
    categorias = []
    
    print(f"DEBUG: work_key={work_key}, edition_keys={edition_keys}")
    
    #Primeiro tentar buscar por edição
    if edition_keys:
        edition_key = edition_keys[0]
        try:
            print(f"DEBUG: Tentando edição: {edition_key}")
            r = requests.get(f"https://openlibrary.org/books/{edition_key}.json", timeout=6)
            if r.status_code == 200:
                data = r.json()
                print(f"DEBUG: Dados da edição: {list(data.keys())}")
                
                # Número de páginas
                paginas = data.get("number_of_pages")
                print(f"DEBUG: Páginas da edição: {paginas}")
                
                # Editora
                publishers = data.get('publishers', [])
                if publishers:
                    if isinstance(publishers[0], dict):
                        publicadora = publishers[0].get('name', '')
                    else:
                        publicadora = publishers[0]
                print(f"DEBUG: Editora da edição: {publicadora}")
                
                # Descrição da edição
                if not sinopse:
                    desc = data.get('description')
                    if desc:
                        if isinstance(desc, dict):
                            sinopse = desc.get('value', '')
                        elif isinstance(desc, str):
                            sinopse = desc
        except Exception as e:
            print(f"DEBUG: Erro na edição: {e}")
            pass
    
    #Se não encontrou tudo, buscar no work
    if not sinopse or not paginas or not publicadora or not categorias:
        try:
            print(f"DEBUG: Tentando work: {work_key}")
            r = requests.get(f"https://openlibrary.org/works/{work_key}.json", timeout=6)
            if r.status_code == 200:
                data = r.json()
                print(f"DEBUG: Dados do work: {list(data.keys())}")
                
                # Sinopse do work
                if not sinopse:
                    desc = data.get("description")
                    if desc:
                        if isinstance(desc, dict):
                            sinopse = desc.get("value") or ""
                        elif isinstance(desc, str):
                            sinopse = desc
                
                # Páginas do work
                if not paginas:
                    paginas = data.get("number_of_pages_median") or data.get("number_of_pages")
                print(f"DEBUG: Páginas do work: {paginas}")
                
                # Editora do work
                if not publicadora:
                    publishers = data.get('publishers', [])
                    if publishers:
                        if isinstance(publishers[0], dict):
                            publicadora = publishers[0].get('name', '')
                        else:
                            publicadora = publishers[0]
                
                # Categorias do work
                if not categorias:
                    subjects = data.get('subjects', [])
                    if subjects:
                        categorias = subjects
                print(f"DEBUG: Categorias do work: {categorias}")
        except Exception as e:
            print(f"DEBUG: Erro no work: {e}")
            pass
    
    #Caso ainda não tenha todas as informações, tentar buscar por ISBN se disponível.
    if edition_keys and (not publicadora or not paginas):
        try:
            print(f"DEBUG: Tentando ISBN: {edition_keys[0]}")
            
            isbn_url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{edition_keys[0]}&jscmd=data&format=json"
            r = requests.get(isbn_url, timeout=6)
            if r.status_code == 200:
                data = r.json()
                isbn_key = f"ISBN:{edition_keys[0]}"
                if isbn_key in data:
                    book_data = data[isbn_key]
                    print(f"DEBUG: Dados do ISBN: {list(book_data.keys())}")
                    
                    # Editora
                    if not publicadora:
                        publishers = book_data.get('publishers', [])
                        if publishers:
                            if isinstance(publishers[0], dict):
                                publicadora = publishers[0].get('name', '')
                            else:
                                publicadora = publishers[0]
                    print(f"DEBUG: Editora do ISBN: {publicadora}")
                    
                    # Páginas
                    if not paginas:
                        paginas = book_data.get('number_of_pages')
                    print(f"DEBUG: Páginas do ISBN: {paginas}")
        except Exception as e:
            print(f"DEBUG: Erro no ISBN: {e}")
            pass
    
    #Tenta buscar por edição usando o endpoint de edições.
    if not publicadora or not paginas:
        try:
            print(f"DEBUG: Tentando endpoint de edições para work: {work_key}")
            r = requests.get(f"https://openlibrary.org/works/{work_key}/editions.json", timeout=6)
            if r.status_code == 200:
                data = r.json()
                entries = data.get('entries', [])
                if entries:
                    # Pega a primeira edição
                    edition_data = entries[0]
                    print(f"DEBUG: Dados da edição via editions: {list(edition_data.keys())}")
                    
                    if not paginas:
                        paginas = edition_data.get('number_of_pages')
                    print(f"DEBUG: Páginas via editions: {paginas}")
                    
                    if not publicadora:
                        publishers = edition_data.get('publishers', [])
                        if publishers:
                            if isinstance(publishers[0], dict):
                                publicadora = publishers[0].get('name', '')
                            else:
                                publicadora = publishers[0]
                    print(f"DEBUG: Editora via editions: {publicadora}")
        except Exception as e:
            print(f"DEBUG: Erro no endpoint editions: {e}")
            pass
    
    print(f"DEBUG: Resultado final - sinopse: {len(sinopse)}, paginas: {paginas}, publicadora: {publicadora}, categorias: {categorias}")
    return sinopse, paginas, publicadora, categorias

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

            for doc in payload.get('docs', [])[:15]:
                
                raw_key = doc.get('key') or ""
                work_key = raw_key.split('/')[-1] if raw_key else None
                if not work_key:
                    continue

                if Livro.objects.filter(externo_ID__in=[work_key, raw_key]).exists():
                    continue

                autor_nome = ", ".join(doc.get('author_name', [])) if doc.get('author_name') else 'Autor não informado'
                autor_obj, _ = Autor.objects.get_or_create(nome=autor_nome)

                edition_keys = doc.get('edition_key', []) or []
                sinopse, paginas, publicadora_detalhada, categorias_api = _ol_fetch_details(work_key, edition_keys)

                if categorias_api:
                    # Pega a primeira categoria da API
                    categoria_nome = categorias_api[0] if categorias_api else 'Categoria não informada'
                else:
                    categoria_nome = ", ".join(doc.get('subject', [])[:3]) if doc.get('subject') else 'Categoria não informada'
                
                categoria_obj, _ = Categoria.objects.get_or_create(nome=categoria_nome)

                if doc.get('first_publish_year'):
                    try:
                        data_pub = datetime(int(doc['first_publish_year']), 1, 1).date()
                    except:
                        data_pub = datetime.now().date()
                else:
                    data_pub = datetime.now().date()

                if not sinopse:
                    fs = doc.get('first_sentence')
                    if isinstance(fs, list):
                        sinopse = fs[0] if fs else ''
                    elif isinstance(fs, dict):
                        sinopse = fs.get('value') or ''
                    elif isinstance(fs, str):
                        sinopse = fs

                if not publicadora_detalhada:
                    publicadora_detalhada = ", ".join(doc.get('publisher', [])) if doc.get('publisher') else 'Editora não informada'

                capa = f"https://covers.openlibrary.org/b/id/{doc.get('cover_i')}-M.jpg" if doc.get('cover_i') else ''

                livro_novo = Livro.objects.create(
                    titulo=doc.get('title', 'Título não disponível'),
                    autor=autor_obj,
                    categoria=categoria_obj,
                    data_publicacao=data_pub,
                    capa=capa,
                    publicadora=publicadora_detalhada,
                    sinopse=sinopse or '',
                    numero_paginas=paginas,
                    externo_ID=work_key, 
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
    
    #Caso ainda tenha dados faltando, ao clicar para visualizar detalhes, tenta mais uma vez pegar informações do livro específico.
    if livro.externo_ID and (not livro.sinopse or not livro.numero_paginas or not livro.publicadora):
        edition_keys = [livro.externo_ID]  # Tentar usar o próprio ID como edição
        sinopse, paginas, publicadora, categorias = _ol_fetch_details(livro.externo_ID, edition_keys)
        
        if sinopse and not livro.sinopse:
            livro.sinopse = sinopse
        if paginas and not livro.numero_paginas:
            livro.numero_paginas = paginas
        if publicadora and not livro.publicadora:
            livro.publicadora = publicadora
        
        livro.save()
    
    return render(request, 'catalogo/detalhes_livro.html', {'livro': livro})