from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from openpyxl import load_workbook
import json
import os
import uuid
import tempfile
from .models import Category, Location, Article
from .forms import ImportExcelForm


# ─────────────────────────────────────────────
#  MAPEO DE CÓDIGOS DE UBICACIÓN
# ─────────────────────────────────────────────
LOCATION_CODES = {
    'RECP': 'Recepción', 'SC': 'Secretaría', 'ECON': 'Economía',
    'CONT': 'Contadora', 'AUXCONT': 'Aux. Contabilidad', 'RECT': 'Rectoría',
    'SD': 'Sala de Docentes', 'SDC': 'Cafetería Docentes',
    'LABIOG': 'Laboratorio de Biología', 'LABFIS': 'Laboratorio de Física',
    'FIS': 'Herramientas de Física', 'DP': 'Deportes', 'ALM': 'Almacén',
    'PS': 'Psicopedagogía', 'CA': 'Coordinación Académica', 'ORT': 'Oratorio',
    'SACR': 'Sacristía', 'CC': 'Coordinación de Convivencia',
    'LABQUI': 'Laboratorio de Química', 'SERVG': 'Cuarto Servicios Generales',
    'TEAT': 'Teatro', 'RT': 'Restaurante/Cafetería', 'SJ': 'Salón de Juegos',
    'PREK': 'Prekinder', 'KIN': 'Kinder', 'JD': 'Jardín', 'TR': 'Transición',
    'PR': 'Primero', 'SG': 'Segundo', 'BT': 'Biblioteca', 'SLT': 'Sala de Lectura',
    'ARCHCONT': 'Archivo Contabilidad', 'TDIPR': 'Sala TDI Primaria',
    'SISBTO': 'Sistemas Bachillerato', 'ROB': 'Robótica',
    'MTOEQUI': 'Cuarto Mto Equipos', 'SIP': 'Sistemas Primaria',
    'TC': 'Tercero', 'CT': 'Cuarto', 'QT': 'Quinto', 'SX': 'Sexto',
    'SP1': '701', 'EF': 'Enfermería', 'TEC': 'Técnicas', 'PAST': 'Pastoral',
    'DIBUJ': 'Salón de Dibujo', 'SP2': '702', 'OC1': '801', 'OC2': '802',
    'NV1': '901', 'LBIN': 'Laboratorio de Inglés', 'NV2': '902',
    'DC1': '1001', 'DC2': '1002', 'ONC1': '1101', 'ONC2': '1102',
    'BAN': 'Cuarto de Banda', 'TDIB': 'Sala TDI Bachillerato',
    'SAUD': 'Audiovisuales', 'DZ': 'Danzas', 'MUS': 'Música',
    'MTO': 'Cuarto de Mantenimiento', 'PAP': 'Útiles, Papelería',
    'VEHIC': 'Vehículos', 'DC': 'Portátiles Docentes',
    'CS': 'Cámaras de Seguridad', 'SUCL4': 'Sillas Universitarias',
    'COM10': 'Elementos Muebles y Enseres', 'COM02': 'Elementos Equipos y Máquinas',
}

TEMP_DIR = tempfile.gettempdir()


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def infer_category_from_sheet_name(sheet_name):
    s = str(sheet_name).lower()
    if any(w in s for w in ['comunidad', 'listado', 'codificacion', 'codificación', 'rosario', 'funza']):
        return None
    if 'papeler' in s or 'útiles' in s or 'utiles' in s: return 'Papelería'
    if 'equipo' in s or 'máquina' in s or 'maquina' in s: return 'Tecnología'
    if 'deport' in s or 'recre' in s: return 'Deportes'
    if 'laboratorio' in s: return 'Ciencias'
    if 'comun' in s or 'radio' in s: return 'Tecnología'
    if 'cocina' in s or 'cafeter' in s: return 'Cocina y Cafetería'
    if 'culto' in s: return 'Elementos de Culto'
    if 'music' in s or 'instrum' in s: return 'Música'
    if 'bibliot' in s or 'audiov' in s or 'medios' in s: return 'Biblioteca'
    if 'mueble' in s or 'ensere' in s: return 'Muebles y Enseres'
    if 'aseo' in s or 'limpieza' in s: return 'Aseo y Limpieza'
    if 'vehiculo' in s or 'vehículo' in s or 'herramient' in s: return 'Construcción y Mantenimiento'
    if 'enfermer' in s: return 'Enfermería'
    if 'uniforme' in s or 'vestuario' in s: return 'Vestuario'
    return 'General'


def detect_status_from_columns(row_data, headers):
    for idx, header in enumerate(headers):
        h = str(header).lower().strip()
        if h in ['bueno', 'estado_bueno'] and len(row_data) > idx:
            if str(row_data[idx]).strip().upper() == 'X': return 'available'
        if h in ['regular', 'estado_regular'] and len(row_data) > idx:
            if str(row_data[idx]).strip().upper() == 'X': return 'maintenance'
        if h in ['malo', 'estado_malo'] and len(row_data) > idx:
            if str(row_data[idx]).strip().upper() == 'X': return 'damaged'
    return 'available'


# ─────────────────────────────────────────────
#  PASO 1: Subir y parsear Excel → JSON en disco
# ─────────────────────────────────────────────

def _parse_excel_to_json(file_path):
    """Lee el Excel completo y devuelve lista de dicts serializables + sheets_info."""
    from datetime import datetime

    wb = load_workbook(file_path, read_only=True, data_only=True)
    all_rows = []
    sheets_info = []
    codigo_counts = {}
    sheet_number = 0

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        category_name = infer_category_from_sheet_name(sheet_name)
        if category_name is None:
            continue

        headers = []
        for cell in ws[8]:
            if cell.value:
                headers.append(str(cell.value).strip())
        if not headers:
            continue

        sheet_number += 1

        codigo_idx   = next((i for i, h in enumerate(headers) if 'codigo'      in h.lower()), None)
        desc_idx     = next((i for i, h in enumerate(headers) if 'descripcion' in h.lower()), None)
        fecha_idx    = next((i for i, h in enumerate(headers) if 'fecha' in h.lower() and 'compra' in h.lower()), None)
        cantidad_idx = next((i for i, h in enumerate(headers) if 'cantidad'    in h.lower()), None)
        valor_idx    = next((i for i, h in enumerate(headers) if 'valor'       in h.lower()), None)
        proveedor_idx = next(
            (i for i, h in enumerate(headers)
             if h and any(w in str(h).lower() for w in ['proveedor', 'comprado', 'lugar'])), 8)

        preview_data = []
        sheet_rows   = 0

        for row_num, row in enumerate(ws.iter_rows(min_row=9, values_only=True), start=9):
            if not any(row):
                continue

            codigo_original = str(row[codigo_idx]).strip() if codigo_idx is not None and len(row) > codigo_idx and row[codigo_idx] else ''
            descripcion     = str(row[desc_idx]).strip()   if desc_idx   is not None and len(row) > desc_idx   and row[desc_idx]   else ''

            if not descripcion or descripcion.lower() in ['none', 'null', '']:
                continue

            # Código único
            if codigo_original:
                codigo_counts[codigo_original] = codigo_counts.get(codigo_original, 0) + 1
                codigo_unico = f"{codigo_original}-{codigo_counts[codigo_original]:04d}"
            else:
                codigo_unico = f"AUTO-{sheet_number:02d}-{row_num:04d}"

            # Cantidad
            cantidad = 1
            if cantidad_idx is not None and len(row) > cantidad_idx and row[cantidad_idx]:
                try:
                    cantidad = int(float(str(row[cantidad_idx]).replace(',', '').strip()))
                except Exception:
                    cantidad = 1

            # Precio
            precio = None
            if valor_idx is not None and len(row) > valor_idx and row[valor_idx]:
                try:
                    ps = str(row[valor_idx]).replace('$', '').replace(',', '').replace('.', '').strip()
                    if ps and ps != 'None':
                        precio = float(ps)
                except Exception:
                    pass

            # Fecha
            fecha_compra = None
            if fecha_idx is not None and len(row) > fecha_idx and row[fecha_idx]:
                try:
                    fv = row[fecha_idx]
                    if isinstance(fv, str):
                        for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%Y']:
                            try:
                                fecha_compra = datetime.strptime(fv.strip(), fmt).strftime('%Y-%m-%d')
                                break
                            except Exception:
                                continue
                    elif hasattr(fv, 'strftime'):
                        fecha_compra = fv.strftime('%Y-%m-%d')
                except Exception:
                    pass

            # Proveedor
            proveedor = None
            if proveedor_idx is not None and len(row) > proveedor_idx and row[proveedor_idx]:
                pv = str(row[proveedor_idx]).strip()
                if pv and pv.lower() not in ['none', 'null', '', 'n/a', '-']:
                    proveedor = pv[:200]

            # Ubicación
            location_name = 'No Especificado'
            location_code = codigo_original.split('.')[0] if '.' in codigo_original else ''
            if location_code and location_code in LOCATION_CODES:
                location_name = LOCATION_CODES[location_code]

            status = detect_status_from_columns(row, headers)

            all_rows.append({
                'name':          descripcion[:200],
                'code':          codigo_unico[:50],
                'category_name': category_name,
                'location_name': location_name,
                'quantity':      max(0, cantidad),
                'status':        status,
                'price':         precio,
                'purchase_date': fecha_compra,
                'supplier':      proveedor,
            })
            sheet_rows += 1

            # Preview (primeras 3 filas)
            if len(preview_data) < 3:
                preview_data.append({
                    'row_number': row_num,
                    'data': [str(v) if v is not None else '' for v in row][:4],
                })

        sheets_info.append({
            'name':      sheet_name,
            'headers':   headers[:6],
            'preview':   preview_data,
            'row_count': sheet_rows,
        })

    wb.close()
    return all_rows, sheets_info


# ─────────────────────────────────────────────
#  VIEWS
# ─────────────────────────────────────────────

@login_required
def import_preview(request):
    if request.method == 'POST' and 'excel_file' in request.FILES:
        excel_file = request.FILES['excel_file']
        file_id    = str(uuid.uuid4())
        xlsx_path  = os.path.join(TEMP_DIR, f'import_{file_id}.xlsx')
        json_path  = os.path.join(TEMP_DIR, f'import_{file_id}.json')

        try:
            # Guardar xlsx
            with open(xlsx_path, 'wb') as f:
                for chunk in excel_file.chunks(chunk_size=1024 * 1024):
                    f.write(chunk)

            # Parsear → JSON
            all_rows, sheets_info = _parse_excel_to_json(xlsx_path)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(all_rows, f, ensure_ascii=False)

            os.remove(xlsx_path)  # ya no necesitamos el xlsx

            request.session['import_file_id']   = file_id
            request.session['import_total_rows'] = len(all_rows)

            return render(request, 'inventory/import_preview_colegio.html', {
                'step':         'preview',
                'sheets_info':  sheets_info,
                'total_sheets': len(sheets_info),
                'total_rows':   len(all_rows),
                'file_id':      file_id,
            })

        except Exception as e:
            for p in [xlsx_path, json_path]:
                try: os.remove(p)
                except: pass
            messages.error(request, f'Error al leer el archivo: {str(e)}')
            return redirect('import_preview')

    return render(request, 'inventory/import_preview_colegio.html', {'step': 'upload'})


@login_required
def import_chunk(request):
    """
    Recibe un chunk de filas en JSON y las inserta.
    Body: { file_id, offset, limit }
    Response: { inserted, total, done }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data   = json.loads(request.body)
        file_id = data.get('file_id')
        offset  = int(data.get('offset', 0))
        limit   = int(data.get('limit', 50))
    except Exception:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)

    json_path = os.path.join(TEMP_DIR, f'import_{file_id}.json')
    if not os.path.exists(json_path):
        return JsonResponse({'error': 'Archivo no encontrado'}, status=404)

    with open(json_path, 'r', encoding='utf-8') as f:
        all_rows = json.load(f)

    total = len(all_rows)
    chunk = all_rows[offset:offset + limit]

    if not chunk:
        # Limpiar archivo
        try: os.remove(json_path)
        except: pass
        return JsonResponse({'inserted': 0, 'total': total, 'done': True})

    # Caches locales por chunk
    category_cache = {}
    location_cache = {}

    def get_category(name):
        if name not in category_cache:
            obj, _ = Category.objects.get_or_create(name__iexact=name, defaults={'name': name})
            category_cache[name] = obj
        return category_cache[name]

    def get_location(name):
        if name not in location_cache:
            obj, _ = Location.objects.get_or_create(name__iexact=name, defaults={'name': name})
            location_cache[name] = obj
        return location_cache[name]

    articles = []
    for row in chunk:
        try:
            a = Article(
                name         = row['name'],
                code         = row['code'],
                category     = get_category(row['category_name']),
                location     = get_location(row['location_name']),
                quantity     = row['quantity'],
                unit         = 'unidad',
                status       = row['status'],
                min_quantity = 1,
                created_by   = request.user,
            )
            if row.get('price'):
                a.price = row['price']
            if row.get('purchase_date'):
                from datetime import date
                a.purchase_date = date.fromisoformat(row['purchase_date'])
            if row.get('supplier'):
                a.supplier = row['supplier']
            articles.append(a)
        except Exception:
            pass

    with transaction.atomic():
        Article.objects.bulk_create(articles, ignore_conflicts=True)

    done = (offset + limit) >= total
    if done:
        try: os.remove(json_path)
        except: pass

    return JsonResponse({
        'inserted': len(articles),
        'total':    total,
        'done':     done,
    })


@login_required
def article_toggle_status(request, pk):
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
                'success': True, 'message': message,
                'new_status': article.status,
                'status_display': article.get_status_display(),
            })
        except Article.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Artículo no encontrado'}, status=404)
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)