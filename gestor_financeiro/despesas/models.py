from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']
    
    def total_mes(self, ano, mes, usuario):
        return self.despesa_set.filter(
            data__year=ano,
            data__month=mes,
            usuario=usuario
        ).aggregate(total=Sum('valor'))['total'] or 0

class Despesa(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"
    
    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-data']
