from django.urls import path
from . import views

app_name = 'compras'

urlpatters = [
    path('finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('historico/', views.historico_compras, name='historico_compras')
]