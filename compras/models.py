from django.db import models
from django.contrib.auth import get_user_model
from catalogo.models import Livro

User = get_user_model()

class Compra(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data_compra = models.DateTimeField(auto_now_add=True)
    endereco = models.CharField(max_length=255)

class ItemCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='itens')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
