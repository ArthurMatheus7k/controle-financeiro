from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('nova/', views.nova_despesa, name='nova_despesa'),
    path('editar/<int:pk>/', views.DespesaUpdate.as_view(), name='editar_despesa'),
    path('excluir/<int:pk>/', views.DespesaDelete.as_view(), name='excluir_despesa'),
    path('exportar/csv/', views.exportar_csv, name='exportar_csv'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
] 