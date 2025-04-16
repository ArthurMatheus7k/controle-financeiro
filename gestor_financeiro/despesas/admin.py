from django.contrib import admin
from .models import Categoria, Despesa

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria', 'valor', 'data', 'usuario')
    list_filter = ('categoria', 'data', 'usuario')
    search_fields = ('descricao',)
    date_hierarchy = 'data'
