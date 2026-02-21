from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from openpyxl import load_workbook
import json
import re
from .models import Category, Location, Article
from .forms import ImportExcelForm


# MAPEO DE CÓDIGOS DE UBICACIÓN
LOCATION_CODES = {
    'RECP': 'Recepción',
    'SC': 'Secretaría',
    'ECON': 'Economía',
    'CONT': 'Contadora',
    'AUXCONT': 'Aux. Contabilidad',
    'RECT': 'Rectoría',
    'SD': 'Sala de Docentes',
    'SDC': 'Cafetería Docentes',
    'LABIOG': 'Laboratorio de Biología',
    'LABFIS': 'Laboratorio de Física',
    'FIS': 'Herramientas de Física',
    'DP': 'Deportes',
    'ALM': 'Almacén',
    'PS': 'Psicopedagogía',
    'CA': 'Coordinación Académica',
    'ORT': 'Oratorio',
    'SACR': 'Sacristía',
    'CC': 'Coordinación de Convivencia',
    'LABQUI': 'Laboratorio de Química',
    'SERVG': 'Cuarto Servicios Generales',
    'TEAT': 'Teatro',
    'RT': 'Restaurante/Cafetería',
    'SJ': 'Salón de Juegos',
    'PREK': 'Prekinder',
    'KIN': 'Kinder',
    'JD': 'Jardín',
    'TR': 'Transición',
    'PR': 'Primero',
    'SG': 'Segundo',
    'BT': 'Biblioteca',
    'SLT': 'Sala de Lectura',
    'ARCHCONT': 'Archivo Contabilidad',
    'TDIPR': 'Sala TDI Primaria',
    'SISBTO': 'Sistemas Bachillerato',
    'ROB': 'Robótica',
    'MTOEQUI': 'Cuarto Mto Equipos',
    'SIP': 'Sistemas Primaria',
    'TC': 'Tercero',
    'CT': 'Cuarto',
    'QT': 'Quinto',
    'SX': 'Sexto',
    'SP1': '701',
    'EF': 'Enfermería',
    'TEC': 'Técnicas',
    'PAST': 'Pastoral',
    'DIBUJ': 'Salón de Dibujo',
    'SP2': '702',
    'OC1': '801',
    'OC2': '802',
    'NV1': '901',
    'LBIN': 'Laboratorio de Inglés',
    'NV2': '902',
    'DC1': '1001',
    'DC2': '1002',
    'ONC1': '1101',
    'ONC2': '1102',
    'BAN': 'Cuarto de Banda',
    'TDIB': 'Sala TDI Bachillerato',
    'SAUD': 'Audiovisuales',
    'DZ': 'Danzas',
    'MUS': 'Música',
    'MTO': 'Cuarto de Mantenimiento',
    'PAP': 'Útiles, Papelería',
    'VEHIC': 'Vehículos',
    'DC': 'Portátiles Docentes',
    'CS': 'Cámaras de Seguridad',
    'SUCL4': 'Sillas Universitarias',
    'COM10': 'Elementos Muebles y Enseres',
    'COM02': 'Elementos Equipos y Máquinas',
}


def infer_category_from_description(description, location_name=''):
    """Inferir categoría basándose en palabras clave - VERSIÓN MEJORADA MÁS ESPECÍFICA"""
    
    desc_lower = description.lower() if description else ''
    loc_lower = location_name.lower() if location_name else ''
    
    # PRIORIDAD 1: Papelería y oficina (muy común en colegios)
    if 'papeler' in loc_lower or 'pap' in loc_lower or 'utiles' in loc_lower or 'útiles' in loc_lower:
        return 'Papelería'
    
    if any(word in desc_lower for word in ['papel', 'hoja', 'cuaderno', 'lapiz', 'lápiz', 'esfero',
                                            'marcador', 'resaltador', 'borrador', 'tijera', 'tijeras',
                                            'grapadora', 'perforadora', 'carpeta', 'folder', 'cinta',
                                            'pegante', 'silicona', 'cartulina', 'cartón', 'pintura',
                                            'colores', 'tempera', 'acuarela', 'pincel', 'mina',
                                            'sacapunta', 'regla', 'compás', 'escuadra', 'clips',
                                            'gancho', 'corrector', 'block', 'acetato', 'papel',
                                            'tinta', 'tajalapiz', 'engrapador']):
        return 'Papelería'
    
    # PRIORIDAD 2: Libros y medios
    if 'bibliot' in loc_lower or 'lectura' in loc_lower:
        return 'Biblioteca'
    
    if any(word in desc_lower for word in ['libro', 'revista', 'enciclopedia', 'memoria', 'actas',
                                            'diccionario', 'atlas', 'texto', 'manual', 'guia']):
        return 'Biblioteca'
    
    # PRIORIDAD 3: Tecnología e informática
    if any(word in loc_lower for word in ['sistemas', 'robot', 'tdi', 'audiovisual', 'informatica']):
        return 'Tecnología'
    
    if any(word in desc_lower for word in ['computador', 'laptop', 'pc', 'monitor', 'teclado', 'mouse', 
                                            'impresora', 'proyector', 'tablet', 'disco', 'router',
                                            'switch', 'cable', 'wifi', 'amplificador', 'parlante', 'micrófono',
                                            'camara', 'cámara', 'transformador', 'dvr', 'voltimetro',
                                            'pantalla', 'cpu', 'scanner', 'usb', 'memoria', 'video',
                                            'audio', 'bocina', 'altavoz', 'auricular', 'bateria',
                                            'cargador', 'adaptador', 'hdmi', 'vga', 'electronico']):
        return 'Tecnología'
    
    # PRIORIDAD 4: Deportes y recreación
    if 'deport' in loc_lower or any(code in loc_lower for code in ['dp', 'recreacion', 'gimnasio']):
        return 'Deportes'
    
    if any(word in desc_lower for word in ['balón', 'balon', 'pelota', 'red', 'cancha', 'aro',
                                            'inflador', 'bomba', 'conos', 'lazo', 'colchoneta', 'cajon',
                                            'baston', 'raqueta', 'guantes', 'casco', 'rodillera',
                                            'futbol', 'basquet', 'voleibol', 'tenis', 'ping', 'pong',
                                            'ajedrez', 'dama', 'juego', 'deporte']):
        return 'Deportes'
    
    # PRIORIDAD 5: Laboratorios y ciencias
    if any(word in loc_lower for word in ['laboratorio', 'lab', 'biolog', 'quimic', 'fisica', 'ciencia']):
        return 'Ciencias'
    
    if any(word in desc_lower for word in ['microscopio', 'probeta', 'beaker', 'tubo', 'pipeta', 'reactivo',
                                            'matraz', 'bureta', 'erlenmeyer', 'embudo', 'pinza',
                                            'mechero', 'balanza', 'termómetro', 'gradilla', 'cristal',
                                            'vidrio', 'laboratorio', 'experimento', 'químico']):
        return 'Ciencias'
    
    # PRIORIDAD 6: Muebles y enseres
    if any(word in desc_lower for word in ['silla', 'mesa', 'escritorio', 'estante', 'anaquel',
                                            'archivo', 'archivador', 'armario', 'locker', 'gabinete', 'pupitre',
                                            'banco', 'sofá', 'butaco', 'mueble', 'tapete', 'alfombra',
                                            'cajonera', 'biblioteca', 'repisa', 'perchero', 'vitrina']):
        return 'Muebles y Enseres'
    
    # PRIORIDAD 7: Cocina y cafetería
    if 'cafeter' in loc_lower or 'cocina' in loc_lower or 'restaurante' in loc_lower or 'comedor' in loc_lower:
        return 'Cocina y Cafetería'
    
    if any(word in desc_lower for word in ['cafetera', 'dispensador', 'nevera', 'estufa', 'horno',
                                            'olla', 'sartén', 'plato', 'vaso', 'taza', 'cuchara',
                                            'tenedor', 'cuchillo', 'bandeja', 'purificador', 'licuadora',
                                            'microondas', 'tetera', 'jarra', 'recipiente']):
        return 'Cocina y Cafetería'
    
    # PRIORIDAD 8: Música e instrumentos
    if 'music' in loc_lower or 'banda' in loc_lower:
        return 'Música'
    
    if any(word in desc_lower for word in ['instrumento', 'guitarra', 'piano', 'batería', 'flauta',
                                            'tambor', 'bombo', 'platillo', 'baqueta', 'trompeta',
                                            'clarinete', 'saxofon', 'violin', 'arpa', 'organo']):
        return 'Música'
    
    # PRIORIDAD 9: Elementos de culto y religiosos
    if 'orator' in loc_lower or 'sacr' in loc_lower or 'capilla' in loc_lower or 'iglesia' in loc_lower:
        return 'Elementos de Culto'
    
    if any(word in desc_lower for word in ['imagen', 'virgen', 'santo', 'cruz', 'cuadro', 'crucifijo',
                                            'sagrado', 'sagrario', 'corazón', 'jesús', 'maría',
                                            'religioso', 'altar', 'vela', 'candelabro']):
        return 'Elementos de Culto'
    
    # PRIORIDAD 10: Aseo y limpieza
    if 'aseo' in loc_lower or 'limpieza' in loc_lower or 'servicio' in loc_lower:
        return 'Aseo y Limpieza'
    
    if any(word in desc_lower for word in ['escoba', 'trapero', 'recogedor', 'balde', 'caneca',
                                            'detergente', 'jabón', 'trapeador', 'cepillo', 'guantes',
                                            'limpiador', 'desinfectante', 'cloro', 'toalla', 'paño']):
        return 'Aseo y Limpieza'
    
    # PRIORIDAD 11: Teatro, danzas y arte
    if 'teatro' in loc_lower or 'danza' in loc_lower or 'arte' in loc_lower:
        return 'Teatro y Danzas'
    
    if any(word in desc_lower for word in ['telón', 'cortina', 'escenario', 'tramoya', 'pendon',
                                            'vestuario', 'disfraz', 'maquillaje', 'utileria']):
        return 'Teatro y Danzas'
    
    # PRIORIDAD 12: Oficina y administración
    if any(word in loc_lower for word in ['secretar', 'recep', 'rector', 'admin', 'oficina', 'coord']):
        return 'Oficina'
    
    if any(word in desc_lower for word in ['sello', 'tampón', 'numerador', 'fechador', 'facturador',
                                            'cosedora', 'calculadora', 'telefono', 'fax']):
        return 'Oficina'
    
    # SI TIENE CÓDIGO DE UBICACIÓN, usar eso como pista
    if 'PAP' in location_name.upper():
        return 'Papelería'
    elif 'LAB' in location_name.upper():
        return 'Ciencias'
    elif 'DEP' in location_name.upper() or 'DP' in location_name.upper():
        return 'Deportes'
    elif 'MUS' in location_name.upper() or 'BAN' in location_name.upper():
        return 'Música'
    elif 'BIB' in location_name.upper() or 'BT' in location_name.upper():
        return 'Biblioteca'
    
    # ÚLTIMO RECURSO: Buscar cualquier palabra común
    palabras_comunes = {
        'plástico': 'Papelería',
        'metalico': 'Muebles y Enseres',
        'madera': 'Muebles y Enseres',
        'cuero': 'Muebles y Enseres',
        'tela': 'Muebles y Enseres',
        'electric': 'Tecnología',
        'manual': 'Biblioteca',
        'didactico': 'Papelería',
        'educativo': 'Papelería',
        'escolar': 'Papelería',
    }
    
    for palabra, categoria in palabras_comunes.items():
        if palabra in desc_lower:
            return categoria
    
    # Default solo si NO hay ninguna coincidencia
    return 'General'


def detect_status_from_columns(row_data, headers):
    """Detectar estado basándose en cuál columna tiene X"""
    
    # Buscar las columnas de estado
    bueno_col = None
    regular_col = None
    malo_col = None
    
    for idx, header in enumerate(headers):
        h_clean = str(header).lower().strip()
        if h_clean in ['bueno', 'estado_bueno']:
            bueno_col = idx
        elif h_clean in ['regular', 'estado_regular']:
            regular_col = idx
        elif h_clean in ['malo', 'estado_malo']:
            malo_col = idx
    
    # Verificar cuál tiene X
    if bueno_col is not None and len(row_data) > bueno_col:
        val = str(row_data[bueno_col]).strip().upper()
        if val in ['X', 'x']:
            return 'available'
    
    if regular_col is not None and len(row_data) > regular_col:
        val = str(row_data[regular_col]).strip().upper()
        if val in ['X', 'x']:
            return 'maintenance'
    
    if malo_col is not None and len(row_data) > malo_col:
        val = str(row_data[malo_col]).strip().upper()
        if val in ['X', 'x']:
            return 'damaged'
    
    return 'available'  # Default


@login_required
def import_preview(request):
    """Vista previa para archivo Excel del colegio con múltiples hojas"""
    
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']
            
            try:
                wb = load_workbook(excel_file, data_only=True)
                
                # Guardar información de todas las hojas
                sheets_info = []
                
                for sheet_name in wb.sheetnames:
                    ws = wb[sheet_name]
                    
                    # Leer encabezados desde fila 8
                    headers = []
                    for cell in ws[8]:
                        if cell.value:
                            headers.append(str(cell.value).strip())
                    
                    if not headers:
                        continue  # Saltar hojas sin encabezados
                    
                    # Leer primeras 5 filas como preview (desde fila 9)
                    preview_data = []
                    for row_idx, row in enumerate(ws.iter_rows(min_row=9, max_row=13, values_only=True), start=9):
                        if any(row):
                            row_data = [str(val) if val is not None else '' for val in row]
                            preview_data.append({
                                'row_number': row_idx,
                                'data': row_data
                            })
                    
                    sheets_info.append({
                        'name': sheet_name,
                        'headers': headers,
                        'preview': preview_data,
                        'row_count': ws.max_row - 8  # Aproximado
                    })
                
                # Guardar en sesión
                import base64
                excel_file.seek(0)
                file_content = excel_file.read()
                request.session['excel_file_content'] = base64.b64encode(file_content).decode('utf-8')
                request.session['excel_filename'] = excel_file.name
                request.session['sheets_info'] = sheets_info
                
                context = {
                    'sheets_info': sheets_info,
                    'total_sheets': len(sheets_info),
                    'step': 'preview'
                }
                
                return render(request, 'inventory/import_preview_colegio.html', context)
                
            except Exception as e:
                messages.error(request, f'Error al leer el archivo: {str(e)}')
                return redirect('import_preview')
        
        elif 'confirm_import' in request.POST:
            # Ejecutar importación
            try:
                import base64
                import io
                
                file_content_b64 = request.session.get('excel_file_content')
                if not file_content_b64:
                    messages.error(request, 'Sesión expirada. Por favor, sube el archivo nuevamente.')
                    return redirect('import_preview')
                
                file_content = base64.b64decode(file_content_b64)
                file_obj = io.BytesIO(file_content)
                
                result = import_colegio_excel(file_obj, request.user)
                
                # Mostrar resultados
                if result['success_count'] > 0:
                    messages.success(request, f'✓ {result["success_count"]} artículos importados exitosamente')
                
                if result['warning_count'] > 0:
                    messages.warning(request, f'⚠ {result["warning_count"]} advertencias')
                
                if result['error_count'] > 0:
                    messages.error(request, f'✗ {result["error_count"]} errores')
                    # Mostrar solo primeros 10 errores
                    for error in result['errors'][:10]:
                        messages.error(request, error)
                    if len(result['errors']) > 10:
                        messages.info(request, f'... y {len(result["errors"]) - 10} errores más')
                
                # Limpiar sesión
                for key in ['excel_file_content', 'excel_filename', 'sheets_info']:
                    request.session.pop(key, None)
                
                return redirect('article_list')
                
            except Exception as e:
                messages.error(request, f'Error en la importación: {str(e)}')
                return redirect('import_preview')
    
    return render(request, 'inventory/import_preview_colegio.html', {
        'step': 'upload'
    })


def import_colegio_excel(file_obj, user):
    """Importar Excel específico del colegio con 15 hojas"""
    
    wb = load_workbook(file_obj, data_only=True)
    
    results = {
        'success_count': 0,
        'error_count': 0,
        'warning_count': 0,
        'errors': [],
        'warnings': []
    }
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Leer encabezados desde fila 8
        headers = []
        for cell in ws[8]:
            if cell.value:
                headers.append(str(cell.value).strip())
        
        if not headers:
            continue
        
        # Detectar índices de columnas importantes
        codigo_idx = next((i for i, h in enumerate(headers) if 'codigo' in h.lower()), None)
        desc_idx = next((i for i, h in enumerate(headers) if 'descripcion' in h.lower()), None)
        fecha_idx = next((i for i, h in enumerate(headers) if 'fecha' in h.lower()), None)
        cantidad_idx = next((i for i, h in enumerate(headers) if 'cantidad' in h.lower()), None)
        valor_idx = next((i for i, h in enumerate(headers) if 'valor' in h.lower()), None)
        
        # Procesar filas desde fila 9
        for row_num, row in enumerate(ws.iter_rows(min_row=9, values_only=True), start=9):
            try:
                if not any(row):
                    continue
                
                # Extraer datos
                codigo = str(row[codigo_idx]).strip() if codigo_idx is not None and len(row) > codigo_idx and row[codigo_idx] else ''
                descripcion = str(row[desc_idx]).strip() if desc_idx is not None and len(row) > desc_idx and row[desc_idx] else ''
                
                # Si no hay descripción válida, saltar
                if not descripcion or descripcion.lower() in ['none', 'null', '']:
                    continue
                
                # Cantidad
                cantidad = 1
                if cantidad_idx is not None and len(row) > cantidad_idx and row[cantidad_idx]:
                    try:
                        cant_str = str(row[cantidad_idx]).replace(',', '').strip()
                        cantidad = int(float(cant_str))
                    except:
                        cantidad = 1
                
                # Precio
                precio = None
                if valor_idx is not None and len(row) > valor_idx and row[valor_idx]:
                    try:
                        precio_str = str(row[valor_idx]).replace('$', '').replace(',', '').replace('.', '').strip()
                        if precio_str and precio_str != 'None':
                            precio = float(precio_str)
                    except:
                        pass
                
                # Detectar ubicación desde el código o nombre de hoja
                location_name = 'No Especificado'
                location_code = codigo.split('.')[0] if '.' in codigo else ''
                
                if location_code in LOCATION_CODES:
                    location_name = LOCATION_CODES[location_code]
                else:
                    # Intentar desde nombre de hoja
                    for code, name in LOCATION_CODES.items():
                        if code.lower() in sheet_name.lower() or name.lower() in sheet_name.lower():
                            location_name = name
                            break
                
                # Obtener o crear ubicación
                location, _ = Location.objects.get_or_create(
                    name__iexact=location_name,
                    defaults={'name': location_name}
                )
                
                # Inferir categoría
                category_name = infer_category_from_description(descripcion, location_name)
                category, _ = Category.objects.get_or_create(
                    name__iexact=category_name,
                    defaults={'name': category_name}
                )
                
                # Detectar estado
                status = detect_status_from_columns(row, headers)
                
                # Crear artículo
                article_data = {
                    'name': descripcion[:200],  # Limitar longitud
                    'code': codigo[:50] if codigo else None,
                    'category': category,
                    'location': location,
                    'quantity': max(0, cantidad),
                    'unit': 'unidad',
                    'status': status,
                    'created_by': user,
                    'min_quantity': 1,
                }
                
                if precio:
                    article_data['price'] = precio
                
                Article.objects.create(**article_data)
                results['success_count'] += 1
                
            except Exception as e:
                results['errors'].append(f"Hoja '{sheet_name}' Fila {row_num}: {str(e)}")
                results['error_count'] += 1
    
    return results


@login_required
def article_toggle_status(request, pk):
    """Habilitar/Deshabilitar artículo (AJAX)"""
    if request.method == 'POST':
        try:
            article = Article.objects.get(pk=pk)
            
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
    
    return render(request, 'inventory/import_preview_colegio.html', {
    'step': 'upload',
    'sheets_info': [],
    'total_sheets': 0
})