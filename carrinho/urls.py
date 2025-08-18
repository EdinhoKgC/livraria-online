from django.urls import path
from . import views

app_name = 'carrinho'

urlpatterns = [
    path('adicionar/<int:livro_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('remover/<int:item_id>/', views.remover_item, name='remover_item'),
    path('aumentar/<int:item_id>/', views.aumentar_quantidade, name='aumentar_quantidade'),
    path('diminuir/<int:item_id>/', views.diminuir_quantidade, name='diminuir_quantidade'),
    path('', views.visualizar_carrinho, name='visualizar_carrinho'),
]