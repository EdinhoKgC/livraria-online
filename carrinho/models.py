from django.db import models
from django.contrib.auth import get_user_model
from catalogo.models import Livro

User = get_user_model()

class Carrinho(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantidade}x {self.livro.titulo}"