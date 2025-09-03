import time
import sys
import io
import traceback
import builtins
from contextlib import redirect_stdout, redirect_stderr
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.html import escape
from django.db import connection
from .models import PythonCommandLog
from django.contrib.auth import get_user_model

# Importar todos os modelos do projeto
from usuarios.models import CustomUser, Endereco, Perfil
from catalogo.models import Livro, Autor, Categoria
from carrinho.models import Carrinho, ItemCarrinho
from compras.models import Compra, ItemCompra

User = get_user_model()

def is_admin(user):
    """Verifica se o usuário é administrador"""
    return user.is_authenticated and (user.is_superuser or user.is_staff)

# Contexto global persistente para cada sessão
_shell_contexts = {}

def get_shell_context(user_id):
    """Retorna o contexto Python persistente para o usuário"""
    if user_id not in _shell_contexts:
        _shell_contexts[user_id] = {
            # Built-ins do Python
            '__builtins__': builtins,
            
            # Módulos padrão
            'sys': sys,
            'time': time,
            'datetime': __import__('datetime'),
            'json': __import__('json'),
            'math': __import__('math'),
            'random': __import__('random'),
            're': __import__('re'),
            'os': __import__('os'),
            'collections': __import__('collections'),
            'itertools': __import__('itertools'),
            'functools': __import__('functools'),
            
            # Django específico
            'connection': connection,
            
            # Modelos Django (importados sob demanda)
            'User': User,
        }
    return _shell_contexts[user_id]

@login_required
@user_passes_test(is_admin)
def python_shell_view(request):
    """View principal do Python Shell"""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        if not code:
            messages.error(request, 'Código não pode estar vazio')
            return redirect('webshell:python_shell')
        
        # Verificar comandos perigosos (lista mais restritiva)
        dangerous_patterns = [
            'import subprocess',
            'import os.system',
            'import sys.exit',
            'exec(',
            'eval(',
            'compile(',
            'open(',
            'file(',
            'input(',
            'raw_input(',
            'exit(',
            'quit(',
            'reload(',
            '__import__(',
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code.lower():
                messages.error(request, f'Comando perigoso detectado: {pattern}')
                return redirect('webshell:python_shell')
        
        try:
            # Executar código Python
            result = execute_python_code(code, request.user.id)
            
            # Salvar log
            PythonCommandLog.objects.create(
                user=request.user,
                command=code,
                output=result['output'],
                error=result['error'],
                execution_time=result['execution_time'],
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Código executado com sucesso')
            return render(request, 'webshell/python_shell.html', {
                'last_code': code,
                'last_output': result['output'],
                'last_error': result['error'],
                'last_execution_time': result['execution_time']
            })
            
        except Exception as e:
            messages.error(request, f'Erro ao executar código: {str(e)}')
            return redirect('webshell:python_shell')
    
    # Buscar histórico de comandos
    recent_logs = PythonCommandLog.objects.filter(user=request.user)[:10]
    
    return render(request, 'webshell/python_shell.html', {
        'recent_logs': recent_logs
    })

def execute_python_code(code, user_id):
    """Executa código Python de forma segura com contexto persistente"""
    start_time = time.time()
    
    # Capturar stdout e stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    output = ""
    error = ""
    
    try:
        # Redirecionar stdout e stderr
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        # Obter contexto persistente do usuário
        global_context = get_shell_context(user_id)
        local_context = {}
        
        # Executar código
        exec(code, global_context, local_context)
        
        # Capturar saída
        output = stdout_capture.getvalue()
        error = stderr_capture.getvalue()
        
        # Se não há saída mas o código foi executado, mostrar resultado da última expressão
        if not output and not error and code.strip():
            # Tentar avaliar a última linha como expressão
            lines = code.strip().split('\n')
            last_line = lines[-1].strip()
            
            # Se a última linha não é um statement (não termina com :)
            if not last_line.endswith(':') and not last_line.startswith(('if ', 'for ', 'while ', 'def ', 'class ', 'try:', 'except', 'finally:', 'with ')):
                try:
                    result = eval(last_line, global_context, local_context)
                    if result is not None:
                        output = repr(result)
                except:
                    pass  # Se não conseguir avaliar, não faz nada
        
    except Exception as e:
        error = traceback.format_exc()
    finally:
        # Restaurar stdout e stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    
    execution_time = time.time() - start_time
    
    return {
        'output': output,
        'error': error,
        'execution_time': execution_time
    }

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
@csrf_exempt
def execute_python_ajax(request):
    """Endpoint AJAX para executar código Python"""
    code = request.POST.get('code', '').strip()
    
    if not code:
        return JsonResponse({'error': 'Código não pode estar vazio'}, status=400)
    
    # Verificar comandos perigosos
    dangerous_patterns = [
        'import subprocess',
        'import os.system',
        'import sys.exit',
        'exec(',
        'eval(',
        'compile(',
        'open(',
        'file(',
        'input(',
        'raw_input(',
        'exit(',
        'quit(',
        'reload(',
        '__import__(',
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code.lower():
            return JsonResponse({
                'error': f'Comando perigoso detectado: {pattern}'
            }, status=403)
    
    try:
        result = execute_python_code(code, request.user.id)
        
        # Salvar log
        PythonCommandLog.objects.create(
            user=request.user,
            command=code,
            output=result['output'],
            error=result['error'],
            execution_time=result['execution_time'],
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return JsonResponse({
            'output': result['output'],
            'error': result['error'],
            'execution_time': result['execution_time'],
            'code': code
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
def command_history(request):
    """Visualizar histórico de comandos Python"""
    logs = PythonCommandLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'webshell/history.html', {'logs': logs})

@login_required
@user_passes_test(is_admin)
def clear_context(request):
    """Limpar contexto Python do usuário"""
    if request.user.id in _shell_contexts:
        del _shell_contexts[request.user.id]
    messages.success(request, 'Contexto Python limpo com sucesso!')
    return redirect('webshell:python_shell')

@login_required
@user_passes_test(is_admin)
def django_orm_examples(request):
    """Página com exemplos de consultas Django ORM"""
    examples = [
        {
            'title': 'Importar modelos Django',
            'code': 'from usuarios.models import CustomUser, Endereco, Perfil\nfrom catalogo.models import Livro, Autor, Categoria\nfrom carrinho.models import Carrinho, ItemCarrinho\nfrom compras.models import Compra, ItemCompra',
            'description': 'Importa todos os modelos do projeto'
        },
        {
            'title': 'Contar usuários',
            'code': 'User.objects.count()',
            'description': 'Conta o total de usuários cadastrados'
        },
        {
            'title': 'Listar todos os livros',
            'code': 'Livro.objects.all()',
            'description': 'Retorna todos os livros'
        },
        {
            'title': 'Buscar livros por título',
            'code': 'Livro.objects.filter(titulo__icontains="python")',
            'description': 'Busca livros que contenham "python" no título'
        },
        {
            'title': 'Usuários com mais compras',
            'code': 'from django.db.models import Count\nUser.objects.annotate(total_compras=Count(\'compra\')).order_by(\'-total_compras\')[:5]',
            'description': 'Lista os 5 usuários com mais compras'
        },
        {
            'title': 'Livros mais vendidos',
            'code': 'from django.db.models import Sum\nLivro.objects.annotate(total_vendido=Sum(\'itemcompra__quantidade\')).order_by(\'-total_vendido\')',
            'description': 'Lista livros ordenados por quantidade vendida'
        },
        {
            'title': 'Criar um novo usuário',
            'code': 'user = User.objects.create_user(email="teste@exemplo.com", password="senha123", first_name="João", last_name="Silva")\nprint(f"Usuário criado: {user.email}")',
            'description': 'Cria um novo usuário no sistema'
        },
        {
            'title': 'Verificar contexto atual',
            'code': 'print("Variáveis disponíveis:")\nfor key in sorted(globals().keys()):\n    if not key.startswith(\'_\'):\n        print(f"  {key}")',
            'description': 'Mostra todas as variáveis disponíveis no contexto'
        }
    ]
    
    return render(request, 'webshell/examples.html', {'examples': examples})