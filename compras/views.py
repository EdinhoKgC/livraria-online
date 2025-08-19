from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Compra, ItemCompra
from carrinho.models import Carrinho
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from usuarios.models import Endereco
from usuarios.forms import EnderecoForm

@login_required(login_url='usuarios:login_view')
def finalizar_compra(request):
    carrinho = Carrinho.objects.filter(user=request.user).first()

    if not carrinho or carrinho.itens.count() == 0:
        return redirect('catalogo:listar_livros')

    if request.method == 'POST':
        endereco_id = request.POST.get('endereco_id')
        novo_endereco = request.POST.get('novo_endereco') == 'true'
        
        if not request.user.enderecos.exists():
            novo_endereco = True
        
        if novo_endereco:
            form = EnderecoForm(request.POST)
            if form.is_valid():
                endereco = form.save(commit=False)
                endereco.user = request.user
                endereco.save()
                endereco_completo = endereco.endereco_completo()
            else:
                enderecos = request.user.enderecos.all()
                return render(request, 'compras/finalizar_compra.html', {
                    'carrinho': carrinho,
                    'enderecos': enderecos,
                    'form': form,
                    'novo_endereco': True
                })
        else:

            if endereco_id:
                try:
                    endereco_obj = get_object_or_404(Endereco, id=endereco_id, user=request.user)
                    endereco_completo = endereco_obj.endereco_completo()
                except:
                    return redirect('compras:finalizar_compra')
            else:
                return redirect('compras:finalizar_compra')

        compra = Compra.objects.create(user=request.user, endereco=endereco_completo)

        for item in carrinho.itens.all():
            ItemCompra.objects.create(compra=compra, livro=item.livro, quantidade=item.quantidade)
            
        carrinho.itens.all().delete()

        return redirect('compras:pedido_confirmado', compra_id=compra.id)

    enderecos = request.user.enderecos.all()
    form = EnderecoForm()
    
    return render(request, 'compras/finalizar_compra.html', {
        'carrinho': carrinho,
        'enderecos': enderecos,
        'form': form,
        'novo_endereco': len(enderecos) == 0
    })

@login_required
def pedido_confirmado(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id, user=request.user)
    return render(request, 'compras/pedido_confirmado.html', {'compra': compra})

@login_required
def historico_compras(request):
    compras = Compra.objects.filter(user=request.user).order_by('-data_compra')
    return render(request, 'compras/historico_compras.html', {'compras': compras})

@login_required
def exportar_lista_compras(request):
    compras = Compra.objects.filter(user=request.user)
    
    html_string = render_to_string('compras/historico_compras_pdf.html', {'compras': compras, 'user': request.user})
    
    arquivo_pdf = weasyprint.HTML(string=html_string).write_pdf()
    
    response = HttpResponse(arquivo_pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename="historico_compras.pdf"'
    
    return response
# Create your views here.
