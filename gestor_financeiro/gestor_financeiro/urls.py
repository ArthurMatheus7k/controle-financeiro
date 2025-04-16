from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Função simples e direta para o logout
def custom_logout(request):
    logout(request)  # Django cuida do logout
    return redirect('login')  # Redirecionamento direto para o login

# Função para redirecionar a tela de sessão encerrada para login
def admin_logout_redirect(request):
    return redirect('login')

# Capturar qualquer URL que contenha a palavra "sessao-encerrada"
def session_closed_redirect(request, *args, **kwargs):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/logout/', admin_logout_redirect),  # Sobrescrever URL de logout do admin
    path('admin/login/', RedirectView.as_view(pattern_name='login')),  # Redirecionar para nossa tela de login
    path('admin/r/(\d+)/(\d+)/', RedirectView.as_view(pattern_name='login')),  # Redirecionar sessão encerrada
    re_path(r'.*sessao-encerrada.*', session_closed_redirect),  # Capturar URLs de sessão encerrada
    path('login/', auth_views.LoginView.as_view(template_name='despesas/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),  # Usar a função personalizada
    path('usuarios/', include('usuarios.urls')),  # Incluir URLs de usuários
    path('', include('despesas.urls')),
]
