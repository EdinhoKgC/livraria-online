from django.urls import path
from . import views

app_name = 'webshell'

urlpatterns = [
    path('', views.python_shell_view, name='python_shell'),
    path('execute/', views.execute_python_ajax, name='execute_python'),
    path('history/', views.command_history, name='command_history'),
    path('examples/', views.django_orm_examples, name='django_examples'),
    path('clear/', views.clear_context, name='clear_context'),
]
