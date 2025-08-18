from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail deve ser informado")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

class Endereco(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enderecos')
    nome_endereco = models.CharField(max_length=100, help_text="Ex: Casa, Trabalho, etc.")
    cep = models.CharField(max_length=9)
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    
    def __str__(self):
        return f"{self.nome_endereco} - {self.rua}, {self.numero}, {self.bairro}, {self.cidade}-{self.estado}"
    
    def endereco_completo(self):
        endereco = f"{self.rua}, {self.numero}"
        if self.complemento:
            endereco += f", {self.complemento}"
        endereco += f", {self.bairro}, {self.cidade}-{self.estado}, CEP: {self.cep}"
        return endereco

class Perfil(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome
