#!/usr/bin/env python
"""
Script para crear datos de prueba en el sistema.
Ejecutar: python manage.py shell < create_sample_data.py
O desde Django shell: exec(open('create_sample_data.py').read())
"""

from django.contrib.auth.models import User
from inventory.models import Category, Location, Article, Movement, Loan
from django.utils import timezone
from datetime import timedelta
import random

print("Creando datos de prueba...\n")

# Crear superusuario si no existe
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✓ Superusuario creado (admin/admin123)")

# Crear usuarios de prueba
users_data = [
    ('profesor1', 'profesor1@escuela.com', 'pass123'),
    ('almacenista', 'almacen@escuela.com', 'pass123'),
]

for username, email, password in users_data:
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(username, email, password)
        print(f"✓ Usuario creado: {username}")

# Crear Categorías
categories_data = [
    {'name': 'Ciencias', 'description': 'Material de laboratorio y ciencias', 'color': '#10B981', 'icon': 'flask'},
    {'name': 'Deportes', 'description': 'Equipo y material deportivo', 'color': '#F59E0B', 'icon': 'basketball-ball'},
    {'name': 'Tecnología', 'description': 'Equipos electrónicos y computación', 'color': '#3B82F6', 'icon': 'laptop'},
    {'name': 'Oficina', 'description': 'Material de oficina y papelería', 'color': '#8B5CF6', 'icon': 'paperclip'},
    {'name': 'Arte', 'description': 'Material artístico y manualidades', 'color': '#EC4899', 'icon': 'palette'},
]

categories = {}
for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults=cat_data
    )
    categories[cat.name] = cat
    if created:
        print(f"✓ Categoría creada: {cat.name}")

# Crear Ubicaciones
locations_data = [
    {'name': 'Laboratorio de Química', 'building': 'A', 'floor': '2', 'room': '201'},
    {'name': 'Laboratorio de Física', 'building': 'A', 'floor': '2', 'room': '202'},
    {'name': 'Gimnasio Principal', 'building': 'B', 'floor': 'PB', 'room': ''},
    {'name': 'Sala de Computación', 'building': 'C', 'floor': '1', 'room': '101'},
    {'name': 'Almacén General', 'building': 'A', 'floor': 'PB', 'room': 'A01'},
    {'name': 'Sala de Arte', 'building': 'B', 'floor': '1', 'room': '105'},
]

locations = {}
for loc_data in locations_data:
    loc, created = Location.objects.get_or_create(
        name=loc_data['name'],
        defaults=loc_data
    )
    locations[loc.name] = loc
    if created:
        print(f"✓ Ubicación creada: {loc.name}")

# Crear Artículos
articles_data = [
    # Ciencias
    {'name': 'Microscopio Digital', 'category': 'Ciencias', 'location': 'Laboratorio de Química', 
     'quantity': 15, 'min_quantity': 10, 'unit': 'unidad', 'price': 250.00,
     'description': 'Microscopio digital con cámara integrada'},
    {'name': 'Tubo de Ensayo', 'category': 'Ciencias', 'location': 'Laboratorio de Química',
     'quantity': 150, 'min_quantity': 50, 'unit': 'pieza', 'price': 2.50},
    {'name': 'Balanza Digital', 'category': 'Ciencias', 'location': 'Laboratorio de Física',
     'quantity': 8, 'min_quantity': 5, 'unit': 'unidad', 'price': 180.00},
    
    # Deportes
    {'name': 'Balón de Fútbol', 'category': 'Deportes', 'location': 'Gimnasio Principal',
     'quantity': 20, 'min_quantity': 10, 'unit': 'pieza', 'price': 35.00},
    {'name': 'Balón de Básquetbol', 'category': 'Deportes', 'location': 'Gimnasio Principal',
     'quantity': 15, 'min_quantity': 8, 'unit': 'pieza', 'price': 45.00},
    {'name': 'Colchoneta', 'category': 'Deportes', 'location': 'Gimnasio Principal',
     'quantity': 30, 'min_quantity': 20, 'unit': 'pieza', 'price': 60.00},
    {'name': 'Red de Voleibol', 'category': 'Deportes', 'location': 'Gimnasio Principal',
     'quantity': 3, 'min_quantity': 2, 'unit': 'unidad', 'price': 120.00},
    
    # Tecnología
    {'name': 'Laptop HP', 'category': 'Tecnología', 'location': 'Sala de Computación',
     'quantity': 25, 'min_quantity': 20, 'unit': 'unidad', 'price': 800.00,
     'description': 'Laptop HP Core i5, 8GB RAM, 256GB SSD'},
    {'name': 'Proyector Epson', 'category': 'Tecnología', 'location': 'Sala de Computación',
     'quantity': 5, 'min_quantity': 3, 'unit': 'unidad', 'price': 450.00},
    {'name': 'Teclado USB', 'category': 'Tecnología', 'location': 'Almacén General',
     'quantity': 40, 'min_quantity': 15, 'unit': 'pieza', 'price': 25.00},
    {'name': 'Mouse Inalámbrico', 'category': 'Tecnología', 'location': 'Almacén General',
     'quantity': 45, 'min_quantity': 20, 'unit': 'pieza', 'price': 18.00},
    
    # Oficina
    {'name': 'Resma de Papel Carta', 'category': 'Oficina', 'location': 'Almacén General',
     'quantity': 50, 'min_quantity': 20, 'unit': 'paquete', 'price': 80.00},
    {'name': 'Marcadores de Pizarrón', 'category': 'Oficina', 'location': 'Almacén General',
     'quantity': 100, 'min_quantity': 30, 'unit': 'pieza', 'price': 15.00},
    {'name': 'Grapadora Industrial', 'category': 'Oficina', 'location': 'Almacén General',
     'quantity': 12, 'min_quantity': 5, 'unit': 'pieza', 'price': 45.00},
    
    # Arte
    {'name': 'Pintura Acrílica', 'category': 'Arte', 'location': 'Sala de Arte',
     'quantity': 60, 'min_quantity': 25, 'unit': 'tubo', 'price': 12.00},
    {'name': 'Pinceles Profesionales', 'category': 'Arte', 'location': 'Sala de Arte',
     'quantity': 80, 'min_quantity': 30, 'unit': 'pieza', 'price': 8.00},
    {'name': 'Lienzo 30x40cm', 'category': 'Arte', 'location': 'Sala de Arte',
     'quantity': 40, 'min_quantity': 15, 'unit': 'pieza', 'price': 25.00},
]

admin_user = User.objects.get(username='admin')
created_articles = []

for art_data in articles_data:
    category_name = art_data.pop('category')
    location_name = art_data.pop('location')
    
    art_data['category'] = categories[category_name]
    art_data['location'] = locations[location_name]
    art_data['created_by'] = admin_user
    art_data['status'] = 'available'
    
    art, created = Article.objects.get_or_create(
        name=art_data['name'],
        defaults=art_data
    )
    created_articles.append(art)
    
    if created:
        # Crear movimiento inicial
        Movement.objects.create(
            article=art,
            movement_type='entry',
            quantity=art.quantity,
            previous_quantity=0,
            new_quantity=art.quantity,
            reason='Carga inicial de inventario',
            user=admin_user
        )
        print(f"✓ Artículo creado: {art.name}")

# Crear algunos préstamos de ejemplo
if created_articles:
    print("\nCreando préstamos de ejemplo...")
    
    # Préstamo activo
    article1 = created_articles[0]
    loan1 = Loan.objects.create(
        article=article1,
        borrower_name='Juan Pérez',
        borrower_id='EST-2024-001',
        borrower_contact='juan.perez@estudiante.com',
        quantity=2,
        due_date=timezone.now() + timedelta(days=7),
        status='active',
        notes='Préstamo para proyecto de ciencias',
        approved_by=admin_user
    )
    article1.quantity -= 2
    article1.save()
    print(f"✓ Préstamo creado para {article1.name}")
    
    # Préstamo vencido
    article2 = created_articles[4] if len(created_articles) > 4 else created_articles[1]
    loan2 = Loan.objects.create(
        article=article2,
        borrower_name='María González',
        borrower_id='EST-2024-002',
        borrower_contact='maria.gonzalez@estudiante.com',
        quantity=1,
        due_date=timezone.now() - timedelta(days=3),
        status='overdue',
        notes='Préstamo para práctica deportiva',
        approved_by=admin_user
    )
    article2.quantity -= 1
    article2.save()
    print(f"✓ Préstamo vencido creado para {article2.name}")

print("\n" + "="*50)
print("✓ Datos de prueba creados exitosamente!")
print("="*50)
print("\nCredenciales:")
print("  Usuario: admin")
print("  Contraseña: admin123")
print("\nPuedes iniciar sesión en: http://localhost:8000/")
