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
    """Inferir categoría - PRIORIDAD A CÓDIGOS DE UBICACIÓN"""
    
    if not description:
        return 'General'
    
    desc_lower = str(description).lower()
    loc_lower = str(location_name).lower() if location_name else ''
    loc_upper = str(location_name).upper() if location_name else ''
    
    # ==================== PRIORIDAD 1: CÓDIGOS DE UBICACIÓN ====================
    # Esto es LO MÁS IMPORTANTE - detectar por código primero
    
    # BIBLIOTECA - Todos los códigos BT*
    if 'BT' in loc_upper:
        return 'Biblioteca'
    
    # PAPELERÍA - Códigos PAP*
    if 'PAP' in loc_upper:
        return 'Papelería'
    
    # DEPORTES - Códigos DP* o DEP*
    if 'DP' in loc_upper or 'DEP' in loc_upper:
        return 'Deportes'
    
    # CIENCIAS - Códigos LAB*
    if 'LAB' in loc_upper:
        return 'Ciencias'
    
    # MÚSICA - Códigos MUS* o BAN*
    if 'MUS' in loc_upper or 'BAN' in loc_upper:
        return 'Música'
    
    # TECNOLOGÍA - Códigos TDI*, SIST*, AV*
    if any(code in loc_upper for code in ['TDI', 'SIST', 'ROBOT', 'AV']):
        return 'Tecnología'
    
    # COCINA - Códigos CAF*, COC*, REST*
    if any(code in loc_upper for code in ['CAF', 'COC', 'REST', 'COMED']):
        return 'Cocina y Cafetería'
    
    # ==================== PRIORIDAD 2: UBICACIÓN EN TEXTO ====================
    
    # Biblioteca por ubicación
    if any(word in loc_lower for word in ['biblioteca', 'bibliot', 'lectura']):
        return 'Biblioteca'
    
    # Deportes por ubicación
    if any(word in loc_lower for word in ['deport', 'gimnasio', 'cancha']):
        return 'Deportes'
    
    # Papelería por ubicación
    if any(word in loc_lower for word in ['papeler', 'utiles', 'útiles']):
        return 'Papelería'
    
    # Ciencias por ubicación
    if any(word in loc_lower for word in ['laboratorio', 'lab', 'biolog', 'quimic', 'fisica']):
        return 'Ciencias'
    
    # Tecnología por ubicación
    if any(word in loc_lower for word in ['sistemas', 'informatica', 'audiovisual']):
        return 'Tecnología'
    
    # Música por ubicación
    if any(word in loc_lower for word in ['music', 'banda']):
        return 'Música'
    
    # Cocina por ubicación
    if any(word in loc_lower for word in ['cafeter', 'cocina', 'restaurante', 'comedor']):
        return 'Cocina y Cafetería'
    
    # Oficina por ubicación
    if any(word in loc_lower for word in ['secretar', 'recep', 'rector', 'admin', 'oficina']):
        return 'Oficina'
    
    # Aseo por ubicación
    if any(word in loc_lower for word in ['aseo', 'limpieza', 'servicio']):
        return 'Aseo y Limpieza'
    
    # Teatro por ubicación
    if any(word in loc_lower for word in ['teatro', 'danza', 'arte']):
        return 'Arte y Teatro'
    
    # Culto por ubicación
    if any(word in loc_lower for word in ['orator', 'sacr', 'capilla', 'iglesia']):
        return 'Elementos de Culto'
    
    # ==================== PRIORIDAD 3: DESCRIPCIÓN ====================
    
    # CONSTRUCCIÓN Y MANTENIMIENTO (NUEVA CATEGORÍA)
    construccion_words = [
        # Eléctricos
        'roseta', 'interruptor', 'bombillo', 'bombilla', 'toma', 'enchufe', 
        'cable', 'alambre', 'switch electrico', 'breaker', 'fusible',
        # Construcción
        'vidrio', 'ventana', 'puerta', 'cerradura', 'chapa', 'bisagra',
        'tornillo', 'tuerca', 'clavo', 'puntilla', 'cemento', 'arena',
        'pintura pared', 'brocha', 'rodillo pintar', 'lija',
        # Plomería
        'tuberia', 'tubería', 'llave agua', 'grifo', 'sifón', 'sifon',
        'codo', 'unión', 'pegante pvc', 'cinta teflón', 'cinta teflon'
    ]
    
    if any(word in desc_lower for word in construccion_words):
        return 'Construcción y Mantenimiento'
    
    # Papelería
    papeleria_words = [
        'papel', 'hoja', 'cuaderno', 'lapiz', 'lápiz', 'esfero', 'marcador', 
        'resaltador', 'borrador', 'tijera', 'grapadora', 'perforadora', 'carpeta',
        'folder', 'cinta', 'pegante', 'silicona', 'cartulina', 'pintura tempera',
        'colores', 'tempera', 'pincel', 'mina', 'sacapunta', 'regla', 'compás',
        'clips', 'corrector', 'block', 'acetato', 'tinta'
    ]
    
    if any(word in desc_lower for word in papeleria_words):
        return 'Papelería'
    
    # Deportes
    deportes_words = [
        'balón', 'balon', 'pelota', 'red', 'cancha', 'aro', 'inflador', 'bomba aire',
        'conos', 'lazo', 'colchoneta', 'cajon', 'baston', 'raqueta', 'guantes deporte',
        'casco', 'futbol', 'fútbol', 'basquet', 'voleibol', 'tenis', 'ping pong',
        'ajedrez', 'uniforme deportivo', 'silbato'
    ]
    
    if any(word in desc_lower for word in deportes_words):
        return 'Deportes'
    
    # Tecnología
    tech_words = [
        'computador', 'laptop', 'pc', 'monitor', 'teclado', 'mouse', 'impresora',
        'proyector', 'tablet', 'disco duro', 'router', 'switch', 'amplificador',
        'parlante', 'micrófono', 'microfono', 'camara', 'cámara', 'transformador',
        'dvr', 'pantalla', 'cpu', 'scanner', 'usb', 'video beam', 'bateria',
        'cargador', 'hdmi', 'vga'
    ]
    
    if any(word in desc_lower for word in tech_words):
        return 'Tecnología'
    
    # Ciencias (equipos de laboratorio)
    ciencias_words = [
        'microscopio', 'probeta', 'beaker', 'tubo ensayo', 'pipeta', 'reactivo',
        'matraz', 'bureta', 'mechero', 'balanza', 'erlenmeyer', 'gradilla',
        'pinza laboratorio'
    ]
    
    if any(word in desc_lower for word in ciencias_words):
        return 'Ciencias'
    
    # Muebles y Enseres
    muebles_words = [
        'silla', 'mesa', 'escritorio', 'estante', 'anaquel', 'archivo', 'armario',
        'locker', 'gabinete', 'pupitre', 'banco', 'sofá', 'sofa', 'butaco', 'mueble',
        'tapete', 'alfombra', 'cajonera', 'repisa', 'perchero', 'vitrina'
    ]
    
    if any(word in desc_lower for word in muebles_words):
        return 'Muebles y Enseres'
    
    # Cocina y Cafetería
    cocina_words = [
        'cafetera', 'dispensador', 'nevera', 'estufa', 'horno', 'olla', 'plato',
        'vaso', 'taza', 'cuchara', 'tenedor', 'cuchillo', 'bandeja', 'purificador',
        'licuadora', 'microondas'
    ]
    
    if any(word in desc_lower for word in cocina_words):
        return 'Cocina y Cafetería'
    
    # Música (instrumentos)
    musica_words = [
        'instrumento', 'guitarra', 'piano', 'batería', 'bateria', 'flauta', 'tambor',
        'bombo', 'platillo', 'baqueta', 'trompeta', 'clarinete', 'saxofon', 'violin'
    ]
    
    if any(word in desc_lower for word in musica_words):
        return 'Música'
    
    # Elementos de Culto
    culto_words = [
        'imagen religiosa', 'virgen', 'santo', 'santa', 'cruz', 'crucifijo',
        'sagrado', 'sagrario', 'altar', 'vela', 'rosario'
    ]
    
    if any(word in desc_lower for word in culto_words):
        return 'Elementos de Culto'
    
    # Aseo y Limpieza
    aseo_words = [
        'escoba', 'trapero', 'recogedor', 'balde', 'caneca', 'detergente', 'jabón',
        'jabon', 'trapeador', 'cepillo limpieza', 'guantes aseo', 'limpiador',
        'desinfectante', 'cloro'
    ]
    
    if any(word in desc_lower for word in aseo_words):
        return 'Aseo y Limpieza'
    
    # Arte y Teatro
    teatro_words = [
        'telón', 'telon', 'cortina escenario', 'escenario', 'tramoya', 'pendon',
        'vestuario', 'disfraz', 'maquillaje teatro'
    ]
    
    if any(word in desc_lower for word in teatro_words):
        return 'Arte y Teatro'
    
    # Oficina
    oficina_words = [
        'sello', 'tampón', 'tampon', 'numerador', 'calculadora', 'telefono',
        'teléfono', 'fax', 'archivador oficina'
    ]
    
    if any(word in desc_lower for word in oficina_words):
        return 'Oficina'
    
    # Default (solo si NO hay coincidencia)
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


def infer_category_from_sheet_name(sheet_name):
    """
    Inferir categoría desde el NOMBRE DE LA HOJA del Excel
    Esto es MÁS CONFIABLE que detectar por descripción
    """
    
    sheet_lower = str(sheet_name).lower()
    
    # Hojas a ignorar
    if any(word in sheet_lower for word in ['comunidad', 'listado', 'codificacion', 'codificación', 'rosario', 'funza']):
        return None  # Ignorar esta hoja
    
    # AGRUPACIÓN 1: Papelería
    if 'papeler' in sheet_lower or 'útiles' in sheet_lower or 'utiles' in sheet_lower:
        return 'Papelería'
    
    # AGRUPACIÓN 2: Tecnología (equipos y máquinas)
    if 'equipo' in sheet_lower or 'máquina' in sheet_lower or 'maquina' in sheet_lower:
        return 'Tecnología'
    
    # AGRUPACIÓN 3: Deportes
    if 'deport' in sheet_lower or 'recre' in sheet_lower:
        return 'Deportes'
    
    # AGRUPACIÓN 4: Ciencias (laboratorio)
    if 'laboratorio' in sheet_lower:
        return 'Ciencias'
    
    # AGRUPACIÓN 5: Tecnología (comunicación y radio)
    if 'comun' in sheet_lower or 'radio' in sheet_lower:
        return 'Tecnología'
    
    # AGRUPACIÓN 6: Cocina y Cafetería
    if 'cocina' in sheet_lower or 'cafeter' in sheet_lower:
        return 'Cocina y Cafetería'
    
    # AGRUPACIÓN 7: Elementos de Culto
    if 'culto' in sheet_lower:
        return 'Elementos de Culto'
    
    # AGRUPACIÓN 8: Música
    if 'music' in sheet_lower or 'instrum' in sheet_lower:
        return 'Música'
    
    # AGRUPACIÓN 9: Biblioteca
    if 'bibliot' in sheet_lower or 'audiov' in sheet_lower or 'medios' in sheet_lower:
        return 'Biblioteca'
    
    # AGRUPACIÓN 10: Muebles y Enseres
    if 'mueble' in sheet_lower or 'ensere' in sheet_lower:
        return 'Muebles y Enseres'
    
    # AGRUPACIÓN 11: Aseo y Limpieza
    if 'aseo' in sheet_lower or 'limpieza' in sheet_lower:
        return 'Aseo y Limpieza'
    
    # AGRUPACIÓN 12: Construcción y Mantenimiento (vehículos y herramientas)
    if 'vehiculo' in sheet_lower or 'vehículo' in sheet_lower or 'herramient' in sheet_lower:
        return 'Construcción y Mantenimiento'
    
    # AGRUPACIÓN 13: Enfermería (NUEVA)
    if 'enfermer' in sheet_lower:
        return 'Enfermería'
    
    # AGRUPACIÓN 14: Vestuario (NUEVA)
    if 'uniforme' in sheet_lower or 'vestuario' in sheet_lower:
        return 'Vestuario'
    
    # AGRUPACIÓN 15: Varios → General
    if 'vario' in sheet_lower:
        return 'General'
    
    # Default
    return 'General'


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
    
    # Contador de hojas procesadas
    sheet_number = 0
    
    # CONTADOR GLOBAL para códigos únicos (OPCIÓN 3)
    # Diccionario: {codigo_original: contador}
    codigo_counts = {}
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Inferir categoría desde el NOMBRE DE LA HOJA
        category_name = infer_category_from_sheet_name(sheet_name)
        
        # Si devuelve None, ignorar esta hoja
        if category_name is None:
            results['warnings'].append(f"Hoja '{sheet_name}' ignorada (no es una agrupación de inventario)")
            results['warning_count'] += 1
            continue
        
        sheet_number += 1
        
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
        
        # Obtener o crear la categoría UNA VEZ por hoja
        category, _ = Category.objects.get_or_create(
            name__iexact=category_name,
            defaults={'name': category_name}
        )
        
        # Procesar filas desde fila 9
        for row_num, row in enumerate(ws.iter_rows(min_row=9, values_only=True), start=9):
            try:
                if not any(row):
                    continue
                
                # Extraer datos
                codigo_original = str(row[codigo_idx]).strip() if codigo_idx is not None and len(row) > codigo_idx and row[codigo_idx] else ''
                descripcion = str(row[desc_idx]).strip() if desc_idx is not None and len(row) > desc_idx and row[desc_idx] else ''
                
                # Si no hay descripción válida, saltar
                if not descripcion or descripcion.lower() in ['none', 'null', '']:
                    continue
                
                # GENERAR CÓDIGO ÚNICO (OPCIÓN 3)
                # Ejemplo: PAP01-0001, PAP01-0002, U9-0001
                if codigo_original:
                    # Incrementar contador para este código
                    if codigo_original not in codigo_counts:
                        codigo_counts[codigo_original] = 0
                    codigo_counts[codigo_original] += 1
                    
                    # Generar código único: {original}-{contador con 4 dígitos}
                    codigo_unico = f"{codigo_original}-{codigo_counts[codigo_original]:04d}"
                else:
                    # Si no hay código, usar AUTO
                    codigo_unico = f"AUTO-{sheet_number:02d}-{row_num:04d}"
                
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
                
                # Detectar ubicación desde el código
                location_name = 'No Especificado'
                location_code = codigo_original.split('.')[0] if '.' in codigo_original else ''
                
                if location_code and location_code in LOCATION_CODES:
                    location_name = LOCATION_CODES[location_code]
                
                # Obtener o crear ubicación
                location, _ = Location.objects.get_or_create(
                    name__iexact=location_name,
                    defaults={'name': location_name}
                )
                
                # Detectar estado
                status = detect_status_from_columns(row, headers)
                
                # Crear artículo
                article_data = {
                    'name': descripcion[:200],  # Limitar longitud
                    'code': codigo_unico[:50],  # Código ÚNICO por contador
                    'category': category,  # Categoría ya determinada por nombre de hoja
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
                error_msg = f"Hoja '{sheet_name}' Fila {row_num}: {str(e)}"
                results['errors'].append(error_msg)
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
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)