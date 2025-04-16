from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from datetime import datetime
import csv
import calendar
import json
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Categoria, Despesa

@login_required
def dashboard(request):
    hoje = datetime.now()
    ano = request.GET.get('ano', hoje.year)
    mes = request.GET.get('mes', hoje.month)
    
    # Converter para inteiros
    ano = int(ano)
    mes = int(mes)
    
    # Obter total por categoria para o mês selecionado
    categorias = Categoria.objects.all()
    for categoria in categorias:
        categoria.total = categoria.total_mes(ano, mes, request.user)
    
    # Calcular total geral
    total_geral = Despesa.objects.filter(
        usuario=request.user,
        data__year=ano,
        data__month=mes
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Calcular porcentagens para barras de progresso
    if total_geral > 0:
        for categoria in categorias:
            if categoria.total > 0:
                categoria.porcentagem = (categoria.total / total_geral) * 100
            else:
                categoria.porcentagem = 0
    
    # Despesas do mês
    despesas = Despesa.objects.filter(
        usuario=request.user,
        data__year=ano,
        data__month=mes
    ).order_by('-data')
    
    # Preparar dados em formato JSON para o gráfico
    categorias_com_valores = [cat for cat in categorias if cat.total > 0]
    categorias_json = json.dumps([{
        'nome': cat.nome,
        'total': float(cat.total)
    } for cat in categorias_com_valores])
    
    # Lista de meses com nomes em português
    nomes_meses = {
        1: 'Janeiro',
        2: 'Fevereiro',
        3: 'Março',
        4: 'Abril',
        5: 'Maio',
        6: 'Junho',
        7: 'Julho',
        8: 'Agosto',
        9: 'Setembro',
        10: 'Outubro',
        11: 'Novembro',
        12: 'Dezembro'
    }
    
    meses_com_nomes = [(m, nomes_meses[m]) for m in range(1, 13)]
    
    # Preparar dados para o template
    context = {
        'categorias': categorias,
        'categorias_json': categorias_json,
        'despesas': despesas,
        'total_geral': total_geral,
        'mes_atual': mes,
        'ano_atual': ano,
        'meses': meses_com_nomes,
        'anos': range(hoje.year - 2, hoje.year + 1),
        'mes_nome': nomes_meses[mes]
    }
    
    return render(request, 'despesas/dashboard.html', context)

@login_required
def nova_despesa(request):
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        data = request.POST.get('data')
        
        categoria = get_object_or_404(Categoria, id=categoria_id)
        
        Despesa.objects.create(
            usuario=request.user,
            categoria=categoria,
            descricao=descricao,
            valor=valor,
            data=data
        )
        
        messages.success(request, 'Despesa adicionada com sucesso!')
        return redirect('dashboard')
    
    categorias = Categoria.objects.all()
    context = {
        'categorias': categorias
    }
    
    return render(request, 'despesas/nova_despesa.html', context)

class DespesaUpdate(LoginRequiredMixin, UpdateView):
    model = Despesa
    template_name = 'despesas/editar_despesa.html'
    fields = ['categoria', 'descricao', 'valor', 'data']
    success_url = reverse_lazy('dashboard')
    
    def get_queryset(self):
        return Despesa.objects.filter(usuario=self.request.user)

class DespesaDelete(LoginRequiredMixin, DeleteView):
    model = Despesa
    template_name = 'despesas/excluir_despesa.html'
    success_url = reverse_lazy('dashboard')
    
    def get_queryset(self):
        return Despesa.objects.filter(usuario=self.request.user)

@login_required
def exportar_csv(request):
    hoje = datetime.now()
    ano = request.GET.get('ano', hoje.year)
    mes = request.GET.get('mes', hoje.month)
    
    # Converter para inteiros
    ano = int(ano)
    mes = int(mes)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="despesas_{mes}_{ano}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Data', 'Categoria', 'Descrição', 'Valor'])
    
    despesas = Despesa.objects.filter(
        usuario=request.user,
        data__year=ano,
        data__month=mes
    ).order_by('-data')
    
    for despesa in despesas:
        writer.writerow([
            despesa.data.strftime('%d/%m/%Y'),
            despesa.categoria.nome,
            despesa.descricao,
            despesa.valor
        ])
    
    return response

@login_required
def exportar_pdf(request):
    hoje = datetime.now()
    ano = request.GET.get('ano', hoje.year)
    mes = request.GET.get('mes', hoje.month)
    
    # Converter para inteiros
    ano = int(ano)
    mes = int(mes)
    
    # Lista de meses com nomes em português
    nomes_meses = {
        1: 'Janeiro',
        2: 'Fevereiro',
        3: 'Março',
        4: 'Abril',
        5: 'Maio',
        6: 'Junho',
        7: 'Julho',
        8: 'Agosto',
        9: 'Setembro',
        10: 'Outubro',
        11: 'Novembro',
        12: 'Dezembro'
    }
    
    # Obter dados
    categorias = Categoria.objects.all()
    for categoria in categorias:
        categoria.total = categoria.total_mes(ano, mes, request.user)
    
    categorias_com_valores = [cat for cat in categorias if cat.total > 0]
    
    total_geral = Despesa.objects.filter(
        usuario=request.user,
        data__year=ano,
        data__month=mes
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    despesas = Despesa.objects.filter(
        usuario=request.user,
        data__year=ano,
        data__month=mes
    ).order_by('-data')
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="despesas_{mes}_{ano}.pdf"'
    
    # Criar o documento PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleH = styles["Heading1"]
    styleH2 = styles["Heading2"]
    
    # Título e cabeçalho
    titulo = Paragraph(f"Relatório de Despesas - {nomes_meses[mes]} de {ano}", styleH)
    elements.append(titulo)
    elements.append(Paragraph(f"Usuário: {request.user.username}", styleN))
    elements.append(Paragraph(f"Data de geração: {hoje.strftime('%d/%m/%Y %H:%M:%S')}", styleN))
    elements.append(Paragraph("<br/><br/>", styleN))
    
    # Resumo por categorias
    elements.append(Paragraph("Resumo por Categorias", styleH2))
    
    dados_categorias = [['Categoria', 'Total (R$)']]
    for categoria in categorias_com_valores:
        dados_categorias.append([categoria.nome, f"R$ {categoria.total:.2f}"])
    
    dados_categorias.append(['Total Geral', f"R$ {total_geral:.2f}"])
    
    tabela_categorias = Table(dados_categorias, colWidths=[doc.width/2.0]*2)
    tabela_categorias.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ]))
    
    elements.append(tabela_categorias)
    elements.append(Paragraph("<br/><br/>", styleN))
    
    # Detalhes das despesas
    elements.append(Paragraph("Detalhamento de Despesas", styleH2))
    
    if despesas:
        dados_despesas = [['Data', 'Descrição', 'Categoria', 'Valor (R$)']]
        
        for despesa in despesas:
            dados_despesas.append([
                despesa.data.strftime('%d/%m/%Y'),
                despesa.descricao,
                despesa.categoria.nome,
                f"R$ {despesa.valor:.2f}"
            ])
        
        tabela_despesas = Table(dados_despesas, colWidths=[doc.width/4.0]*4)
        tabela_despesas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ]))
        
        elements.append(tabela_despesas)
    else:
        elements.append(Paragraph("Nenhuma despesa registrada para este período.", styleN))
    
    # Rodapé
    elements.append(Paragraph("<br/><br/>", styleN))
    elements.append(Paragraph("Gestor Financeiro - Sistema de Controle de Despesas", 
                             ParagraphStyle(name='Footer', parent=styleN, alignment=1)))
    
    # Gerar PDF
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
