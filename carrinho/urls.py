from django.urls import path
from . import views

app_name = 'carrinho'

urlpatterns = [
    path('adicionar/<int:livro_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('remover/<int:livro_id>', views.remover_item, name='remover_item'),
    path('', views.visualizar_carrinho, name='visualizar_carrinho'),
]