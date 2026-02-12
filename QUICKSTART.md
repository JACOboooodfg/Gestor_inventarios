# Sistema de Inventario Escolar - Guía Rápida

## 🚀 Inicio Rápido

### 1. Instalar y Ejecutar (Local)

```bash
# Descomprimir el proyecto
cd school_inventory

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar PostgreSQL
# Ver README.md para comandos SQL

# Copiar y configurar .env
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# (Opcional) Cargar datos de prueba
python manage.py shell < create_sample_data.py

# Ejecutar servidor
python manage.py runserver
```

Acceder a: http://localhost:8000

---

## 📦 Características Principales

### ✅ Gestión de Artículos
- Crear, editar, eliminar artículos
- Búsqueda avanzada con filtros
- Alertas automáticas de stock bajo
- Código de barras y fotos
- Precios y valor total del inventario

### ✅ Categorías y Ubicaciones
- Organización flexible por categorías
- Ubicaciones jerárquicas (Edificio > Piso > Salón)
- Estadísticas por categoría

### ✅ Movimientos
- Registro de entradas y salidas
- Ajustes de inventario
- Transferencias entre ubicaciones
- Historial completo con trazabilidad

### ✅ Sistema de Préstamos
- Préstamos con fecha de devolución
- Alertas de préstamos vencidos
- Datos del solicitante
- Estado de préstamos (activo/devuelto/vencido)

### ✅ Importar/Exportar Excel
- Importación masiva desde Excel
- Exportación con formato profesional
- Plantillas incluidas

### ✅ Reportes
- Dashboard con estadísticas en tiempo real
- Reportes por categoría
- Historial de movimientos
- Alertas del sistema

---

## 🎯 Casos de Uso Comunes

### Registrar Nuevos Artículos

1. **Opción A: Uno por uno**
   - Click en "Artículos" → "Nuevo Artículo"
   - Llenar formulario
   - Guardar

2. **Opción B: Importar desde Excel**
   - Preparar archivo Excel con columnas:
     - nombre, categoria, cantidad, ubicacion, descripcion
   - Click en "Importar Excel"
   - Subir archivo
   - Revisar y confirmar

### Registrar una Salida

1. Dashboard → "Registrar Movimiento"
2. Seleccionar artículo
3. Tipo: "Salida"
4. Cantidad
5. Motivo (ej: "Préstamo a Laboratorio A")
6. Guardar

### Hacer un Préstamo

1. Dashboard → "Nuevo Préstamo"
2. Seleccionar artículo
3. Datos del solicitante
4. Cantidad y fecha de devolución
5. Guardar

El sistema automáticamente:
- Reduce el stock
- Registra el movimiento
- Crea alerta si se vence

### Devolver un Préstamo

1. "Préstamos" → Buscar préstamo activo
2. Click en "Devolver"
3. Confirmar

El sistema automáticamente:
- Incrementa el stock
- Marca como devuelto
- Registra la devolución

### Generar Reporte

1. "Reportes" → Seleccionar tipo
2. Aplicar filtros (fecha, categoría, etc.)
3. Click en "Exportar a Excel"
4. Descargar archivo

---

## 👥 Roles y Permisos

### Administrador (Superuser)
- Acceso total al sistema
- Crear/editar/eliminar todo
- Gestionar usuarios
- Ver todos los reportes

### Staff
- Registrar movimientos y préstamos
- Ver reportes
- No puede eliminar artículos

### Viewer (Opcional)
- Solo lectura
- Ver inventario y reportes
- No puede modificar nada

---

## 💡 Tips y Mejores Prácticas

### Organización
- Define categorías antes de cargar artículos
- Usa ubicaciones específicas (no genéricas)
- Mantén códigos de artículos consistentes

### Stock
- Configura cantidades mínimas realistas
- Revisa alertas semanalmente
- Haz inventarios físicos periódicamente

### Préstamos
- Siempre pide identificación del solicitante
- Configura fechas de devolución realistas
- Haz seguimiento a préstamos vencidos

### Backups
```bash
# Hacer backup semanal
pg_dump school_inventory > backup_$(date +%Y%m%d).sql

# O usar el script incluido
python manage.py dumpdata > backup.json
```

### Seguridad
- Cambia SECRET_KEY en producción
- Usa contraseñas fuertes
- Activa HTTPS en producción
- Backups automáticos

---

## 🐛 Solución de Problemas

### Error: "No module named 'crispy_forms'"
```bash
pip install -r requirements.txt
```

### Error: "Database connection failed"
- Verifica que PostgreSQL esté corriendo
- Revisa credenciales en .env
- Verifica que la BD exista

### Estilos no cargan
```bash
python manage.py collectstatic
```

### Migraciones pendientes
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 📞 Soporte

### Logs del Sistema
```bash
# Ver logs en tiempo real
tail -f /var/log/nginx/error.log
sudo journalctl -u school_inventory -f
```

### Comandos Útiles

```bash
# Ver usuarios
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()

# Resetear contraseña
python manage.py changepassword admin

# Ejecutar tests
python manage.py test

# Limpiar sesiones antiguas
python manage.py clearsessions
```

---

## 🔄 Actualizaciones

```bash
# Actualizar código
git pull

# Instalar nuevas dependencias
pip install -r requirements.txt

# Ejecutar nuevas migraciones
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Reiniciar servidor
sudo systemctl restart school_inventory
```

---

## 📊 Ejemplo de Workflow Completo

### Inicio de Año Escolar

1. **Configuración inicial**
   - Crear categorías principales
   - Definir ubicaciones (edificios, salones)
   - Importar inventario desde Excel

2. **Operación diaria**
   - Registrar préstamos cuando sea necesario
   - Registrar devoluciones
   - Monitorear alertas de stock bajo

3. **Fin de semana**
   - Revisar préstamos vencidos
   - Contactar solicitantes
   - Hacer backup de base de datos

4. **Fin de mes**
   - Generar reportes por categoría
   - Exportar movimientos a Excel
   - Analizar consumo

5. **Fin de año**
   - Inventario físico completo
   - Ajustar diferencias
   - Generar reporte anual
   - Backup completo

---

## 🎓 Recursos Adicionales

- **Documentación Django**: https://docs.djangoproject.com/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **PostgreSQL**: https://www.postgresql.org/docs/

---

**¿Necesitas ayuda?**
- Revisa el README.md para instalación
- Consulta DEPLOYMENT.md para despliegue
- Los comentarios en el código explican cada función
