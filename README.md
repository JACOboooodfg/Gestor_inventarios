# Sistema de Gestión de Inventario Escolar

Sistema completo de inventario con Django, PostgreSQL y Tailwind CSS.

## 🌟 Características Nuevas (v2.0)

### ✨ Importación Inteligente de Excel
- **Detección automática de columnas** - No importa cómo nombres tus columnas
- **Vista previa antes de importar** - Revisa tus datos antes de guardar
- **Mapeo flexible** - El sistema sugiere automáticamente el mapeo correcto
- **Validación en tiempo real** - Te muestra exactamente qué filas tienen problemas
- **Creación automática de categorías** - No necesitas crear categorías primero

### 🔀 Habilitar/Deshabilitar Artículos
- **Toggle rápido** sin eliminar permanentemente
- **Filtros por estado** - Ver solo artículos activos o inactivos
- **Historial preservado** - Los artículos deshabilitados mantienen su historial

### 🔍 Búsqueda y Filtros Avanzados
- **Búsqueda instantánea** por nombre, código o descripción
- **Filtros combinables** - Categoría + Estado + Ubicación
- **Exportación filtrada** - Exporta solo lo que ves

## Características Principales

- ✅ Autenticación y roles de usuario (Admin, Staff, Viewer)
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Gestión de categorías y artículos
- ✅ Historial completo de movimientos
- ✅ Sistema de préstamos con fecha de devolución
- ✅ Importar/Exportar a Excel
- ✅ Alertas de stock bajo
- ✅ Búsqueda avanzada y filtros
- ✅ Reportes detallados
- ✅ Interfaz moderna con Tailwind CSS

## Instalación

### ⚡ Inicio Rápido (Nuevo en VSCode)

**¿Primera vez con Django o VSCode nuevo?** → Lee **[INSTALACION_COMPLETA.md](INSTALACION_COMPLETA.md)**

Incluye:
- ✅ Instalación paso a paso desde cero
- ✅ Configuración de PostgreSQL para principiantes
- ✅ Solución de problemas comunes
- ✅ Guía de VSCode
- ✅ Comandos explicados

### 🚀 Instalación Rápida (Si ya sabes Django)

### 1. Clonar o descargar el proyecto

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL

Crear base de datos en PostgreSQL:

```sql
CREATE DATABASE school_inventory;
CREATE USER school_admin WITH PASSWORD 'tu_password_seguro';
ALTER ROLE school_admin SET client_encoding TO 'utf8';
ALTER ROLE school_admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE school_admin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE school_inventory TO school_admin;
```

### 5. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```
SECRET_KEY=tu-secret-key-super-segura
DEBUG=True
DB_NAME=school_inventory
DB_USER=school_admin
DB_PASSWORD=tu_password_seguro
DB_HOST=localhost
DB_PORT=5432
```

### 6. Ejecutar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear superusuario

```bash
python manage.py createsuperuser
```

### 8. Cargar datos de ejemplo (opcional)

```bash
python manage.py loaddata initial_data.json
```

### 9. Ejecutar servidor

```bash
python manage.py runserver
```

Acceder a: `http://localhost:8000`

## Estructura del Proyecto

```
school_inventory/
├── config/                 # Configuración del proyecto
├── inventory/             # App principal
│   ├── models.py          # Modelos de BD
│   ├── views.py           # Vistas
│   ├── forms.py           # Formularios
│   ├── urls.py            # URLs
│   └── utils.py           # Utilidades (Excel import/export)
├── templates/             # Plantillas HTML
├── static/               # Archivos estáticos
└── media/                # Archivos subidos

```

## Uso

### Roles de Usuario

- **Admin**: Acceso total, crear/editar/eliminar todo
- **Staff**: Registrar movimientos, préstamos, ver reportes
- **Viewer**: Solo lectura

### Importar desde Excel

1. Preparar archivo Excel con columnas: `nombre`, `categoria`, `cantidad`, `ubicacion`, `descripcion`
2. Ir a "Importar Artículos"
3. Subir archivo
4. Revisar vista previa
5. Confirmar importación

### Exportar a Excel

- Desde cualquier listado, click en "Exportar a Excel"
- Se descarga archivo con todos los datos filtrados

## Despliegue

Para Railway.app, Render.com o similar:

1. Configurar variables de entorno
2. Cambiar `DEBUG=False`
3. Configurar `ALLOWED_HOSTS`
4. Usar Gunicorn: `gunicorn config.wsgi:application`

## Licencia

MIT License
