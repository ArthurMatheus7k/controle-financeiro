from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes Bootstrap aos campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-control bg-white',
            'style': 'border: 1px solid #ced4da; height: 46px;'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control bg-white',
            'style': 'border: 1px solid #ced4da; height: 46px;'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control bg-white',
            'style': 'border: 1px solid #ced4da; height: 46px;'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control bg-white',
            'style': 'border: 1px solid #ced4da; height: 46px;'
        })

def cadastro(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}! Agora você pode fazer login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'usuarios/cadastro.html', {'form': form}) 