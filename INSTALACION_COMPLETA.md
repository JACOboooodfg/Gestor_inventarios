# 🚀 GUÍA COMPLETA - DESDE CERO EN VSCODE

## ✅ PRERREQUISITOS

### 1. Instalar Software Base

#### Windows:
1. **Python 3.11+**
   - Descarga: https://www.python.org/downloads/
   - ⚠️ **MUY IMPORTANTE**: Marca "Add Python to PATH" durante instalación
   - Verifica: `python --version` en CMD

2. **PostgreSQL**
   - Descarga: https://www.postgresql.org/download/windows/
   - Durante instalación:
     - Puerto: 5432 (default)
     - Usuario: postgres
     - **ANOTA LA CONTRASEÑA** que configures
   - Verifica: Busca "SQL Shell (psql)" en menú inicio

3. **Git**
   - Descarga: https://git-scm.com/download/win
   - Instalación con opciones por defecto

4. **VSCode**
   - Descarga: https://code.visualstudio.com/
   - Instala extensiones recomendadas:
     - Python (Microsoft)
     - Django (Baptiste Darthenay)

#### Linux (Ubuntu/Debian):
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python
sudo apt install python3 python3-pip python3-venv -y

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Instalar Git
sudo apt install git -y

# Instalar VSCode
# Descarga desde: https://code.visualstudio.com/
```

#### Mac:
```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar dependencias
brew install python@3.11
brew install postgresql
brew install git

# Instalar VSCode desde: https://code.visualstudio.com/
```

---

## 📁 PASO 1: CONFIGURAR PROYECTO

### 1.1 Descomprimir y Abrir en VSCode

```bash
# 1. Descomprime school_inventory.zip en alguna carpeta
#    Por ejemplo: C:\Users\TuUsuario\Proyectos\school_inventory

# 2. Abre VSCode

# 3. File → Open Folder → Selecciona 'school_inventory'

# 4. Abre la terminal integrada:
#    View → Terminal (o Ctrl + `)
```

### 1.2 Crear Entorno Virtual

**Windows (PowerShell):**
```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno
.\venv\Scripts\Activate.ps1

# Si da error de permisos, ejecuta esto primero:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Deberías ver (venv) al inicio de la línea
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Instalar Dependencias

```bash
# Con el entorno virtual activado (debes ver (venv)):
pip install -r requirements.txt

# Si da error de conexión:
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

---

## 🗄️ PASO 2: CONFIGURAR BASE DE DATOS

### 2.1 Crear Base de Datos en PostgreSQL

**Windows:**
```powershell
# Abre "SQL Shell (psql)" desde el menú inicio
# Presiona Enter para todos los valores por defecto
# Cuando pida contraseña, ingresa la que configuraste en la instalación
```

**Linux/Mac:**
```bash
sudo -u postgres psql
```

**Comandos SQL (todos los sistemas):**
```sql
-- Crear base de datos
CREATE DATABASE school_inventory;

-- Crear usuario
CREATE USER school_admin WITH PASSWORD 'MiPassword123!';

-- Configurar usuario
ALTER ROLE school_admin SET client_encoding TO 'utf8';
ALTER ROLE school_admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE school_admin SET timezone TO 'UTC';

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE school_inventory TO school_admin;

-- Salir
\q
```

### 2.2 Configurar Variables de Entorno

```bash
# En VSCode, copia el archivo de ejemplo:
# Windows:
copy .env.example .env

# Linux/Mac:
cp .env.example .env
```

**Edita el archivo .env** (click en el archivo en VSCode):

```bash
SECRET_KEY=django-insecure-cambiar-esto-en-produccion-xyz789
DEBUG=True
DB_NAME=school_inventory
DB_USER=school_admin
DB_PASSWORD=MiPassword123!
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
```

⚠️ **Usa tu contraseña real de PostgreSQL**

---

## 🔧 PASO 3: INICIALIZAR DJANGO

### 3.1 Ejecutar Migraciones

```bash
# Asegúrate de estar en la carpeta del proyecto y con venv activado

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
```

### 3.2 Crear Superusuario

```bash
python manage.py createsuperuser

# Ingresa los datos:
Username: admin
Email address: admin@ejemplo.com
Password: admin123
Password (again): admin123
```

### 3.3 Cargar Datos de Prueba (Opcional)

```bash
# Opción 1: Usando el script
python manage.py shell < create_sample_data.py

# Opción 2: Manualmente en shell
python manage.py shell
>>> exec(open('create_sample_data.py').read())
>>> exit()
```

---

## ▶️ PASO 4: EJECUTAR SERVIDOR

```bash
# Inicia el servidor de desarrollo
python manage.py runserver

# Verás algo como:
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK.
```

**¡Listo!** Abre tu navegador en: **http://localhost:8000**

**Credenciales de login:**
- Usuario: `admin`
- Contraseña: `admin123`

---

## 🎯 CARACTERÍSTICAS MEJORADAS

### ✨ Importación Inteligente de Excel

1. **Dashboard → Importar Excel** (botón naranja)

2. **Funcionalidades:**
   - ✅ **Detección automática de columnas** - Usa cualquier nombre de columna
   - ✅ **Vista previa antes de importar** - Revisa tus datos
   - ✅ **Mapeo flexible** - Arrastra y suelta para mapear campos
   - ✅ **Validación inteligente** - Te dice qué filas tienen errores
   - ✅ **Creación automática de categorías** - No necesitas crearlas primero

3. **Ejemplo de Excel válido:**
   ```
   | Nombre del Producto | Tipo      | Stock | Almacén         |
   |---------------------|-----------|-------|-----------------|
   | Microscopio         | Ciencias  | 10    | Lab. Química    |
   | Balón Fútbol        | Deportes  | 25    | Gimnasio        |
   ```

   El sistema detectará automáticamente que:
   - "Nombre del Producto" → campo `nombre`
   - "Tipo" → campo `categoria`
   - "Stock" → campo `cantidad`
   - "Almacén" → campo `ubicacion`

### 🔀 Habilitar/Deshabilitar Artículos

En la **lista de artículos**, verás un ícono de toggle (🔘):
- **Click** para deshabilitar un artículo sin eliminarlo
- Los artículos deshabilitados aparecen en gris
- Pueden volver a habilitarse con otro click

### 🔍 Búsqueda y Filtros Avanzados

**En Artículos:**
- Buscar por nombre, código o descripción
- Filtrar por categoría
- Filtrar por estado (disponible, en uso, dañado, etc.)
- Filtrar por ubicación
- Combinar múltiples filtros

**Exportar resultados filtrados:**
- Los filtros aplicados se exportan a Excel
- Útil para reportes específicos

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "python no se reconoce como comando"
```bash
# Windows: Reinstala Python y marca "Add Python to PATH"
# O agrega manualmente a PATH:
# Panel de Control → Sistema → Variables de entorno
# Agregar: C:\Python311\ y C:\Python311\Scripts\
```

### Error: "pip no se reconoce como comando"
```bash
python -m pip install --upgrade pip
```

### Error: "connection to server failed"
**PostgreSQL no está corriendo:**

Windows:
```powershell
# Busca "Services" en menú inicio
# Busca "postgresql-x64-XX"
# Click derecho → Start
```

Linux:
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Error: "FATAL: password authentication failed"
**Contraseña incorrecta en .env:**
```bash
# Edita .env con la contraseña correcta de PostgreSQL
DB_PASSWORD=TuPasswordReal
```

### Error: "No module named 'crispy_forms'"
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Estilos no se ven
```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### Error: "Port 8000 already in use"
```bash
# Usa otro puerto
python manage.py runserver 8001

# O mata el proceso anterior:
# Windows:
netstat -ano | findstr :8000
taskkill /PID [número_de_proceso] /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

---

## 📊 FLUJO DE TRABAJO TÍPICO

### 1. Configuración Inicial (Una vez)
```bash
# Crear categorías
Dashboard → Categorías → Nueva Categoría
- Ciencias (color verde)
- Deportes (color naranja)
- Tecnología (color azul)

# Crear ubicaciones
Dashboard → Ubicaciones → Nueva Ubicación
- Laboratorio de Química (Edificio A, Piso 2)
- Gimnasio (Edificio B, Planta Baja)
- Almacén General (Edificio A, Planta Baja)
```

### 2. Cargar Inventario
```bash
# Opción A: Excel masivo
1. Prepara tu Excel con las columnas que tengas
2. Dashboard → Importar Excel
3. Sube archivo
4. Revisa el mapeo automático
5. Confirma e importa

# Opción B: Uno por uno
Dashboard → Nuevo Artículo
```

### 3. Operación Diaria
```bash
# Registrar préstamos
Préstamos → Nuevo Préstamo

# Registrar movimientos
Movimientos → Registrar Movimiento

# Revisar alertas
Campana (🔔) en la parte superior
```

### 4. Reportes
```bash
# Exportar inventario
Artículos → Aplicar filtros → Exportar a Excel

# Ver estadísticas
Dashboard (muestra todo en tiempo real)

# Reportes avanzados
Reportes → Seleccionar tipo
```

---

## 🚀 SIGUIENTE NIVEL

### Desplegar a Internet (Gratis)

#### Opción 1: Railway.app (Recomendado)
```bash
# 1. Crea cuenta en railway.app
# 2. New Project → Deploy from GitHub
# 3. Railway crea PostgreSQL automáticamente
# 4. Configura variables de entorno en Settings
# 5. Deploy automático

# Ver: DEPLOYMENT.md para detalles
```

#### Opción 2: Render.com
- Igual de fácil que Railway
- 90 días gratis de PostgreSQL
- Ver DEPLOYMENT.md

#### Opción 3: Servidor Local/Escuela
- Instala en una PC de la escuela
- Acceso por red local
- Costo: $0
- Ver DEPLOYMENT.md sección "Servidor Local"

---

## 📞 COMANDOS ÚTILES

```bash
# Ver usuarios
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()
>>> exit()

# Cambiar contraseña
python manage.py changepassword admin

# Crear backup
# Windows:
pg_dump -U school_admin school_inventory > backup.sql

# Linux/Mac:
pg_dump school_inventory > backup.sql

# Restaurar backup
psql -U school_admin school_inventory < backup.sql

# Ver logs
# En desarrollo, aparecen en la terminal donde corrió runserver

# Limpiar sesiones antiguas
python manage.py clearsessions
```

---

## ✅ CHECKLIST DE INSTALACIÓN

- [ ] Python 3.11+ instalado
- [ ] PostgreSQL instalado y corriendo
- [ ] Git instalado
- [ ] VSCode instalado
- [ ] Proyecto descomprimido
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Base de datos creada en PostgreSQL
- [ ] Archivo .env configurado
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Servidor corriendo
- [ ] Login exitoso en http://localhost:8000

---

## 🎓 RECURSOS

- **Django Docs**: https://docs.djangoproject.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Python Docs**: https://docs.python.org/3/

---

**¿Problemas?** Revisa la sección "SOLUCIÓN DE PROBLEMAS" arriba.

**¿Todo funcionando?** ¡Empieza a gestionar tu inventario! 🎉
