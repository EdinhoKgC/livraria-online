from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.listar_livros, name='listar_livros'),
    path('livro/<int:livro_id>/', views.detalhes_livro, name='detalhes_livro'),
]