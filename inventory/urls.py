from django.urls import path, include
from . import views
from .import_views import import_preview, import_execute, article_toggle_status

urlpatterns = [
    # Autenticación
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Categorías
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('categories/<int:pk>/inventory/', views.category_inventory, name='category_inventory'),
    path('categories/<int:pk>/export/', views.category_export, name='category_export'),
    path('categories/<int:pk>/import/', views.category_import, name='category_import'),
    
    # Ubicaciones
    path('locations/', views.location_list, name='location_list'),
    path('locations/create/', views.location_create, name='location_create'),
    path('locations/<int:pk>/update/', views.location_update, name='location_update'),
    path('locations/<int:pk>/delete/', views.location_delete, name='location_delete'),
    
    # Artículos
    path('articles/', views.article_list, name='article_list'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('articles/create/', views.article_create, name='article_create'),
    path('articles/<int:pk>/update/', views.article_update, name='article_update'),
    path('articles/<int:pk>/delete/', views.article_delete, name='article_delete'),
    path('articles/<int:pk>/toggle-status/', article_toggle_status, name='article_toggle_status'),
    
    # Movimientos
    path('movements/', views.movement_list, name='movement_list'),
    path('movements/create/', views.movement_create, name='movement_create'),
    
    # Préstamos
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/create/', views.loan_create, name='loan_create'),
    path('loans/<int:pk>/return/', views.loan_return, name='loan_return'),
    
    # Importar/Exportar (Mejorado)
    path('import/', import_preview, name='import_preview'),
    path('import/execute/', import_execute, name='import_execute'),
    path('import/legacy/', views.import_articles, name='import_articles'),  # Mantener versión antigua
    path('export/articles/', views.export_articles, name='export_articles'),
    path('export/movements/', views.export_movements, name='export_movements'),
    path('export/loans/', views.export_loans, name='export_loans'),
    
    # Alertas
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/<int:pk>/read/', views.alert_mark_read, name='alert_mark_read'),
    path('alerts/read-all/', views.alert_mark_all_read, name='alert_mark_all_read'),
    path('', include('social_django.urls', namespace='social')),
    # Reportes
    path('reports/', views.reports, name='reports'),
]