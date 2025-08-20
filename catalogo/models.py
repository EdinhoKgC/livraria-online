from django.db import models

# Create your models here.
class Autor(models.Model):
    nome = models.CharField(blank=True)

    def __str__(self):
        return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=500)

    def __str__(self):
        return self.nome

class Livro(models.Model):
    titulo = models.CharField(max_length=500)
    autor = models.ForeignKey(Autor, on_delete=models.SET_NULL, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    data_publicacao = models.DateField()
    capa = models.URLField()
    sinopse = models.TextField(blank=True)
    numero_paginas = models.IntegerField(blank=True, null=True)
    publicadora = models.CharField(max_length=500, blank=True)
    externo_ID = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.titulo