from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from openpyxl import load_workbook
import json
from .models import Category, Location, Article
from .forms import ImportExcelForm


@login_required
def import_preview(request):
    """Vista previa de importación con mapeo de columnas"""
    
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            # Paso 1: Cargar archivo y mostrar preview
            excel_file = request.FILES['excel_file']
            
            try:
                wb = load_workbook(excel_file)
                ws = wb.active
                
                # Leer encabezados (primera fila)
                headers = []
                for cell in ws[1]:
                    if cell.value:
                        headers.append({
                            'original': str(cell.value),
                            'clean': str(cell.value).lower().strip().replace(' ', '_')
                        })
                
                # Leer primeras 10 filas como preview
                preview_data = []
                for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=11, values_only=True), start=2):
                    if any(row):  # Solo si la fila tiene datos
                        row_data = {}
                        for idx, value in enumerate(row):
                            if idx < len(headers):
                                row_data[headers[idx]['clean']] = value
                        preview_data.append({
                            'row_number': row_idx,
                            'data': row_data
                        })
                
                # Guardar en sesión para el siguiente paso
                request.session['excel_headers'] = headers
                request.session['excel_preview'] = preview_data
                request.session['excel_filename'] = excel_file.name
                
                # Sugerencias de mapeo automático
                field_mappings = suggest_field_mappings(headers)
                
                # Obtener categorías y ubicaciones existentes
                categories = list(Category.objects.values('id', 'name'))
                locations = list(Location.objects.values('id', 'name'))
                
                context = {
                    'headers': headers,
                    'preview_data': preview_data,
                    'field_mappings': field_mappings,
                    'categories': categories,
                    'locations': locations,
                    'step': 'preview'
                }
                
                return render(request, 'inventory/import_preview.html', context)
                
            except Exception as e:
                messages.error(request, f'Error al leer el archivo: {str(e)}')
                return redirect('import_articles')
        
        elif 'confirm_mapping' in request.POST:
            # Paso 2: Confirmar mapeo e importar
            mapping = json.loads(request.POST.get('column_mapping', '{}'))
            headers = request.session.get('excel_headers', [])
            
            # Re-cargar el archivo (en producción usarías almacenamiento temporal)
            # Por ahora, pedimos que suban de nuevo o guardamos en sesión
            
            messages.info(request, 'Función de importación mejorada en proceso')
            return redirect('article_list')
    
    else:
        form = ImportExcelForm()
    
    return render(request, 'inventory/import_articles_enhanced.html', {
        'form': form,
        'step': 'upload'
    })


def suggest_field_mappings(headers):
    """Sugerir mapeo automático de columnas"""
    
    # Mapeo de posibles nombres de columnas a campos del modelo
    field_suggestions = {
        'nombre': ['nombre', 'name', 'articulo', 'item', 'producto', 'descripcion'],
        'codigo': ['codigo', 'code', 'cod', 'sku', 'id'],
        'categoria': ['categoria', 'category', 'cat', 'tipo', 'type'],
        'ubicacion': ['ubicacion', 'location', 'lugar', 'almacen', 'bodega'],
        'cantidad': ['cantidad', 'quantity', 'stock', 'qty', 'existencia'],
        'unidad': ['unidad', 'unit', 'medida', 'um'],
        'cantidad_minima': ['cantidad_minima', 'min_quantity', 'minimo', 'min', 'stock_minimo'],
        'precio': ['precio', 'price', 'costo', 'valor', 'cost'],
        'estado': ['estado', 'status', 'condicion'],
        'codigo_barras': ['codigo_barras', 'barcode', 'ean', 'upc'],
        'descripcion': ['descripcion', 'description', 'desc', 'detalle'],
        'notas': ['notas', 'notes', 'observaciones', 'comentarios'],
    }
    
    mappings = {}
    
    for header in headers:
        clean_name = header['clean']
        best_match = None
        
        # Buscar coincidencia
        for field_name, possible_names in field_suggestions.items():
            if clean_name in possible_names:
                best_match = field_name
                break
        
        mappings[header['original']] = {
            'suggested': best_match,
            'original': header['original'],
            'clean': clean_name
        }
    
    return mappings


@login_required
def import_execute(request):
    """Ejecutar importación con el mapeo confirmado"""
    
    if request.method != 'POST':
        return redirect('import_preview')
    
    try:
        # Obtener mapeo de columnas
        column_mapping = json.loads(request.POST.get('column_mapping', '{}'))
        excel_file = request.FILES.get('excel_file_confirm')
        
        if not excel_file:
            messages.error(request, 'Archivo no encontrado. Por favor sube el archivo nuevamente.')
            return redirect('import_preview')
        
        # Procesar el archivo
        wb = load_workbook(excel_file)
        ws = wb.active
        
        success_count = 0
        error_count = 0
        errors = []
        
        # Leer encabezados
        headers = [str(cell.value) for cell in ws[1] if cell.value]
        
        # Procesar cada fila
        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                # Construir diccionario con los datos mapeados
                mapped_data = {}
                for idx, header in enumerate(headers):
                    if header in column_mapping and idx < len(row):
                        field_name = column_mapping[header]
                        if field_name and field_name != 'ignore':
                            mapped_data[field_name] = row[idx]
                
                # Validar datos requeridos
                if not mapped_data.get('nombre'):
                    errors.append(f"Fila {row_num}: Nombre es requerido")
                    error_count += 1
                    continue
                
                # Procesar categoría
                category = None
                if mapped_data.get('categoria'):
                    cat_name = str(mapped_data['categoria']).strip()
                    category, _ = Category.objects.get_or_create(
                        name__iexact=cat_name,
                        defaults={'name': cat_name}
                    )
                
                # Procesar ubicación
                location = None
                if mapped_data.get('ubicacion'):
                    loc_name = str(mapped_data['ubicacion']).strip()
                    try:
                        location = Location.objects.get(name__iexact=loc_name)
                    except Location.DoesNotExist:
                        pass
                
                # Crear artículo
                article_data = {
                    'name': str(mapped_data['nombre']).strip(),
                    'category': category,
                    'location': location,
                    'quantity': int(mapped_data.get('cantidad', 0)),
                    'unit': str(mapped_data.get('unidad', 'unidad')).strip(),
                    'min_quantity': int(mapped_data.get('cantidad_minima', 5)),
                    'status': mapped_data.get('estado', 'available'),
                    'description': str(mapped_data.get('descripcion', '')).strip(),
                    'notes': str(mapped_data.get('notas', '')).strip(),
                    'created_by': request.user,
                }
                
                # Campos opcionales
                if mapped_data.get('codigo'):
                    article_data['code'] = str(mapped_data['codigo']).strip()
                
                if mapped_data.get('precio'):
                    try:
                        article_data['price'] = float(mapped_data['precio'])
                    except (ValueError, TypeError):
                        pass
                
                if mapped_data.get('codigo_barras'):
                    article_data['barcode'] = str(mapped_data['codigo_barras']).strip()
                
                # Crear artículo
                Article.objects.create(**article_data)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Fila {row_num}: {str(e)}")
                error_count += 1
        
        # Mensajes de resultado
        if success_count > 0:
            messages.success(request, f'✓ {success_count} artículos importados exitosamente')
        
        if error_count > 0:
            messages.warning(request, f'⚠ {error_count} filas con errores')
            for error in errors[:10]:  # Mostrar solo los primeros 10 errores
                messages.error(request, error)
        
        return redirect('article_list')
        
    except Exception as e:
        messages.error(request, f'Error en la importación: {str(e)}')
        return redirect('import_preview')


@login_required
def article_toggle_status(request, pk):
    """Habilitar/Deshabilitar artículo (AJAX)"""
    if request.method == 'POST':
        try:
            article = Article.objects.get(pk=pk)
            
            # Toggle entre available y retired
            if article.status == 'available':
                article.status = 'retired'
                message = f'{article.name} deshabilitado'
            else:
                article.status = 'available'
                message = f'{article.name} habilitado'
            
            article.save()
            
            return JsonResponse({
                'success': True,
                'message': message,
                'new_status': article.status,
                'status_display': article.get_status_display()
            })
        except Article.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Artículo no encontrado'
            }, status=404)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
