from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('pedido-confirmado/<int:compra_id>/', views.pedido_confirmado, name='pedido_confirmado'),
    path('historico/', views.historico_compras, name='historico_compras'),
    path('exportar_pdf/', views.exportar_lista_compras, name='exportar_lista_compras'),
]