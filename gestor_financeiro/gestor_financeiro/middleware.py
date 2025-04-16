from django.shortcuts import redirect
from django.urls import reverse

class LoginRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Verificar se estamos na página de logout ou sessão encerrada do admin
        if (request.path.startswith('/admin/logout/') or 
            'Sessão encerrada' in str(response.content) or 
            response.status_code == 500):
            return redirect(reverse('login'))
        
        return response 