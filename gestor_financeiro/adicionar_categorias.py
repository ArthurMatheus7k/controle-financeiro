import os
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestor_financeiro.settings')
django.setup()

from despesas.models import Categoria

# Lista de categorias padrão
categorias = [
    {"nome": "Alimentação", "descricao": "Gastos com supermercado, restaurantes e delivery"},
    {"nome": "Moradia", "descricao": "Aluguel, condomínio, água, luz, internet, IPTU"},
    {"nome": "Transporte", "descricao": "Combustível, transporte público, táxi, aplicativos"},
    {"nome": "Saúde", "descricao": "Plano de saúde, medicamentos, consultas, exames"},
    {"nome": "Educação", "descricao": "Mensalidades escolares, cursos, livros, material escolar"},
    {"nome": "Lazer", "descricao": "Cinema, viagens, restaurantes, eventos"},
    {"nome": "Vestuário", "descricao": "Roupas, calçados, acessórios"},
    {"nome": "Outros", "descricao": "Despesas diversas que não se encaixam nas categorias anteriores"}
]

# Criar categorias
categorias_criadas = 0
for categoria in categorias:
    obj, created = Categoria.objects.get_or_create(
        nome=categoria["nome"],
        defaults={"descricao": categoria["descricao"]}
    )
    if created:
        categorias_criadas += 1
        print(f"Categoria '{categoria['nome']}' criada com sucesso.")
    else:
        print(f"Categoria '{categoria['nome']}' já existe.")

print(f"\nTotal de categorias criadas: {categorias_criadas}")
print(f"Total de categorias disponíveis: {Categoria.objects.count()}") 