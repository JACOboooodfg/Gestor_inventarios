# inventory/chatbot_views.py
import json
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, F, FloatField, ExpressionWrapper
from django.utils import timezone
from datetime import timedelta
from decouple import config

from .models import (
    Article, Category, Location, Movement,
    AseoProducto, PapeleriaProducto
)

GEMINI_API_KEY = config('AIzaSyBUBSnMucMeL3MX-gCzNqo3QpaAKVgYF1g', default='')
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY
)


def _build_inventory_context():
    """Arma un resumen real del inventario para pasarle a Gemini como contexto."""

    # ── Categorías con totales ──────────────────────────────────
    categorias = list(
        Category.objects.annotate(
            total_items=Count('articles'),
            total_qty=Sum('articles__quantity'),
            valor=Sum(
                ExpressionWrapper(
                    F('articles__quantity') * F('articles__price'),
                    output_field=FloatField()
                )
            )
        ).values('name', 'total_items', 'total_qty', 'valor')
    )

    # ── Stock bajo ──────────────────────────────────────────────
    stock_bajo = list(
        Article.objects.filter(quantity__lte=F('min_quantity'))
        .select_related('category', 'location')
        .values('name', 'code', 'quantity', 'min_quantity',
                'category__name', 'location__name')[:20]
    )

    # ── Movimientos recientes ───────────────────────────────────
    movimientos = list(
        Movement.objects.select_related('article', 'user')
        .order_by('-created_at')
        .values('movement_type', 'quantity', 'article__name',
                'reason', 'created_at')[:10]
    )
    for m in movimientos:
        if m['created_at']:
            m['created_at'] = m['created_at'].strftime('%Y-%m-%d %H:%M')

    # ── Resumen aseo y papelería ────────────────────────────────
    aseo_bajo = list(
        AseoProducto.objects.filter(quantity__lte=F('min_quantity'))
        .values('name', 'quantity', 'min_quantity')[:10]
    )
    papeleria_bajo = list(
        PapeleriaProducto.objects.filter(quantity__lte=F('min_quantity'))
        .values('name', 'quantity', 'min_quantity')[:10]
    )

    total_articulos = Article.objects.count()
    total_categorias = Category.objects.count()
    total_ubicaciones = Location.objects.count()

    return {
        'total_articulos': total_articulos,
        'total_categorias': total_categorias,
        'total_ubicaciones': total_ubicaciones,
        'categorias': categorias,
        'stock_bajo': stock_bajo,
        'movimientos_recientes': movimientos,
        'aseo_stock_bajo': aseo_bajo,
        'papeleria_stock_bajo': papeleria_bajo,
    }


SYSTEM_PROMPT = """
Eres el asistente del Sistema de Inventario del Colegio. 
Ayudas a los usuarios a entender cómo funciona el sistema y a consultar datos del inventario.

## MÓDULOS DEL SISTEMA

### Inventario General
- **Artículos**: Cada artículo tiene código, nombre, categoría, ubicación, cantidad, estado y precio.
- **Estados posibles**: Disponible, En uso, En mantenimiento, Dañado, Dado de baja.
- **Categorías**: Agrupan artículos (Tecnología, Deportes, Ciencias, Muebles, etc.). Cada una tiene color e ícono.
- **Ubicaciones**: Salones, laboratorios, oficinas del colegio. Pueden tener edificio, piso y salón.

### Cómo importar artículos desde Excel
1. Ir a **Importar** en el menú.
2. Subir el archivo `.xlsx`. El sistema lee desde la **fila 8** (encabezados) y fila 9 en adelante (datos).
3. El sistema detecta automáticamente la categoría según el nombre de la hoja.
4. La ubicación se infiere del código del artículo (ej: `LAB.001` → Laboratorio).
5. Se muestra una **vista previa** antes de confirmar la importación.
6. La importación se hace por **chunks de 50** artículos para no bloquear el servidor.
7. Si un código ya existe, se omite (`ignore_conflicts=True`).

### Movimientos
- Tipos: Entrada, Salida, Ajuste, Transferencia, Préstamo, Devolución.
- Cada movimiento guarda cantidad anterior y nueva para trazabilidad.
- Se registran automáticamente al crear artículos o hacer préstamos.

### Préstamos
- Se registra quién solicita, cantidad, fecha de devolución esperada.
- Los préstamos vencidos cambian automáticamente a estado "Vencido".
- Al devolver, la cantidad regresa al artículo y se registra el movimiento.

### Inventario de Aseo
- Módulo separado para productos de limpieza (litros, galones, rollos, etc.).
- Tiene su propio historial de movimientos.
- Accesible desde **Selección de Inventario** → Aseo.

### Inventario de Papelería
- Similar al de aseo pero para útiles de oficina y papelería.
- Unidades: Caja, Paquete, Resma, Rollo, etc.

### Alertas
- Se generan automáticamente cuando el stock baja del mínimo.
- También para préstamos vencidos y artículos en mantenimiento.

### Exportar
- Artículos, movimientos y préstamos se pueden exportar a Excel desde sus respectivas secciones.

### Dashboard
- Muestra stats globales y una gráfica aleatoria entre: cantidad por categoría, top precios, movimientos del mes, valor por categoría/ubicación.

## REGLAS
- Responde siempre en español.
- Sé conciso pero completo.
- Si preguntan por datos reales, úsalos del contexto JSON que se te pasa.
- Si no sabes algo del sistema, dilo claramente.
- Usa listas o pasos numerados cuando expliques procesos.
"""


@login_required
def chatbot_ask(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        body = json.loads(request.body)
        pregunta = body.get('message', '').strip()
        historial = body.get('history', [])  # [{role, text}, ...]
    except Exception:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)

    if not pregunta:
        return JsonResponse({'error': 'Mensaje vacío'}, status=400)

    if not GEMINI_API_KEY:
        return JsonResponse({'error': 'API key de Gemini no configurada'}, status=500)

    # Contexto real del inventario
    ctx = _build_inventory_context()
    context_json = json.dumps(ctx, ensure_ascii=False, default=str)

    # Armar contents para Gemini
    # Primer turno: system prompt + contexto + pregunta del usuario
    contents = []

    # Historial previo
    for msg in historial[-6:]:  # máx 6 turnos anteriores
        role = 'user' if msg['role'] == 'user' else 'model'
        contents.append({'role': role, 'parts': [{'text': msg['text']}]})

    # Turno actual: inyectamos contexto solo en la pregunta actual
    user_text = (
        f"{SYSTEM_PROMPT}\n\n"
        f"## DATOS ACTUALES DEL INVENTARIO\n```json\n{context_json}\n```\n\n"
        f"Usuario pregunta: {pregunta}"
        if not historial  # solo en el primer mensaje
        else pregunta
    )

    contents.append({'role': 'user', 'parts': [{'text': user_text}]})

    payload = {
        'contents': contents,
        'generationConfig': {
            'temperature': 0.4,
            'maxOutputTokens': 1024,
        },
    }

    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        answer = data['candidates'][0]['content']['parts'][0]['text']
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Gemini tardó demasiado, intenta de nuevo'}, status=504)
    except Exception as e:
        return JsonResponse({'error': f'Error al consultar Gemini: {str(e)}'}, status=500)

    return JsonResponse({'answer': answer})