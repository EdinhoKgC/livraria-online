# Livraria Online

Sistema web completo para gerenciamento de uma livraria online, desenvolvido com Django e PostgreSQL, incluindo funcionalidades para catálogo de livros, gerenciamento de carrinho, usuários e finalização de compras, integração com API externa OpenLibrary e geração de PDFs.

---

## Funcionalidades

- Cadastro e login de usuários (com perfil customizado)  
- Catálogo de livros com busca, filtros e paginação  
- Integração com API OpenLibrary para importação e exibição de livros  
- Carrinho de compras com suporte a usuários autenticados e anônimos  
- Finalização de compra com seleção e cadastro de endereços  
- Exportação do histórico de compras em PDF usando WeasyPrint  
- Tratamento de datas com timezone correto  
- Interfaces responsivas com Bootstrap

---

## Tecnologias

- Python 3.13  
- Django 4.2.0
- PostgreSQL 17  
- Bootstrap 5  
- WeasyPrint para exportação de PDFs  
- Requests para consumo da API OpenLibrary

---

## Instalação e configuração

### Pré-requisitos

- Python 3.13 instalado  
- PostgreSQL instalado e configurado  
- Ambiente virtual Python (`venv`)

### Passos para rodar localmente

1. Clone o repositório:  
```
git clone https://github.com/EdinhoKgC/livraria-online.git
cd livraria_online
```

2. Crie e ative o ambiente virtual:  
- Windows:
  ```
  python -m venv venv
  venv\Scripts\activate
  ```
- Linux/macOS:
  ```
  python3 -m venv venv
  source venv/bin/activate
  ```

3. Instale as dependências:  
```
pip install -r requirements.txt
```


4. Configure o banco de dados no `settings.py` (ajuste usuário, senha e host conforme seu ambiente).
- Caso use o PostgreSQL, será necessário instalar a dependencia abaixo:
```
pip install psycopg2-binary
```

6. Rode as migrações:  
```
python manage.py makemigrations
python manage.py migrate
```

6. Crie um superusuário:  
```
python manage.py createsuperuser
```
- será solicitado email e senha.


7. Execute o servidor de desenvolvimento:  
```
python manage.py runserver
```

8. Acesse `http://localhost:8000` no navegador.

---

## Dependências especiais

- Para usar o WeasyPrint no Windows, instale o GTK runtime:  
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

---

## Uso

- Acessar o catálogo, carrinho, login, cadastro e finalizar compras.  
- Busque livros usando filtros por título, autor ou categoria, com importação direta da API OpenLibrary.  
- Visualize o histórico e exporte suas compras em PDF.

---

## Testes e desenvolvimento

- Lembre-se de ativar o ambiente virtual antes de rodar comandos Django.  
- Atualize as dependências com:  
```
pip install --upgrade -r requirements.txt
```
- Caso realize mudança, execute novamente os comandos para gerar as migrations:  
```
python manage.py makemigrations
python manage.py migrate
```

---

## Créditos e referências

- Django Framework: https://www.djangoproject.com/  
- OpenLibrary API: https://openlibrary.org/developers/api  
- WeasyPrint: https://weasyprint.org/

---
