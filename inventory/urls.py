from django.urls import path, include
from . import views
from .import_views import import_preview, article_toggle_status

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
    
    # Importar/Exportar (Especializado para Colegio)
    path('import/', import_preview, name='import_preview'),
    path('import/preview/', import_preview, name='import_preview'),
    # NOTA: import_execute ya no existe - todo se maneja en import_preview
    path('import/legacy/', views.import_articles, name='import_articles'),  # Mantener versión antigua
    path('export/articles/', views.export_articles, name='export_articles'),
    path('export/movements/', views.export_movements, name='export_movements'),
    path('export/loans/', views.export_loans, name='export_loans'),
    
    # Alertas
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/<int:pk>/read/', views.alert_mark_read, name='alert_mark_read'),
    path('alerts/read-all/', views.alert_mark_all_read, name='alert_mark_all_read'),
    
    # Social Auth
    path('', include('social_django.urls', namespace='social')),
    
    # Reportes
    path('reports/', views.reports, name='reports'),
    
    # Utilidades - Borrar todos los artículos
    path('articles/delete-all/confirm/', views.delete_all_articles_confirm, name='delete_all_articles_confirm'),
    path('articles/delete-all/execute/', views.delete_all_articles_execute, name='delete_all_articles_execute'),
    # Selector de inventario
    path('select/', views.select_inventory, name='select_inventory'),

    # Categorías con ubicaciones
    path('categories-locations/', views.category_list_with_locations, name='category_list_with_locations'),
    path('categories/<int:category_pk>/location/<int:location_pk>/', views.category_location_articles, name='category_location_articles'),

    # Dashboard de Aseo
    path('aseo/', views.aseo_dashboard, name='aseo_dashboard'),
    path('aseo/ajustar/<int:pk>/', views.aseo_ajustar_cantidad, name='aseo_ajustar_cantidad'),
    path('aseo/crear/', views.aseo_crear_producto, name='aseo_crear_producto'),
]