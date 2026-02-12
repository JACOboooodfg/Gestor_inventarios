# Guía de Despliegue

## Opción 1: Railway.app (Recomendado)

### Paso 1: Preparar el repositorio
```bash
git init
git add .
git commit -m "Initial commit"
```

### Paso 2: Crear cuenta en Railway
1. Ve a https://railway.app
2. Regístrate con GitHub
3. Click en "New Project"
4. Selecciona "Deploy from GitHub repo"
5. Selecciona tu repositorio

### Paso 3: Agregar PostgreSQL
1. En tu proyecto, click "New"
2. Selecciona "Database" → "PostgreSQL"
3. Railway creará automáticamente la base de datos

### Paso 4: Configurar Variables de Entorno
En Settings → Variables, agrega:
```
SECRET_KEY=tu-key-super-secreta-generada
DEBUG=False
ALLOWED_HOSTS=*.railway.app
DB_NAME=railway
DB_USER=(automático de Railway)
DB_PASSWORD=(automático de Railway)
DB_HOST=(automático de Railway)
DB_PORT=5432
```

### Paso 5: Desplegar
1. Railway desplegará automáticamente
2. Ejecuta las migraciones desde el terminal de Railway:
```bash
python manage.py migrate
python manage.py createsuperuser
```

3. Accede a tu aplicación en la URL que Railway te proporciona

---

## Opción 2: Render.com

### Paso 1: Crear cuenta y nuevo Web Service
1. Ve a https://render.com
2. Click "New" → "Web Service"
3. Conecta tu repositorio de GitHub

### Paso 2: Configuración
- **Name**: school-inventory
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn config.wsgi:application`

### Paso 3: Agregar PostgreSQL
1. En Dashboard, click "New" → "PostgreSQL"
2. Copia la URL de conexión

### Paso 4: Variables de Entorno
```
SECRET_KEY=tu-key-secreta
DEBUG=False
DATABASE_URL=(de PostgreSQL de Render)
ALLOWED_HOSTS=*.onrender.com
```

---

## Opción 3: Servidor Local/Escuela

### Requisitos
- Ubuntu Server 20.04+ o similar
- 2GB RAM mínimo
- Python 3.11+

### Instalación

1. **Instalar dependencias del sistema**
```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx
```

2. **Configurar PostgreSQL**
```bash
sudo -u postgres psql

CREATE DATABASE school_inventory;
CREATE USER school_admin WITH PASSWORD 'tu_password_seguro';
ALTER ROLE school_admin SET client_encoding TO 'utf8';
ALTER ROLE school_admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE school_admin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE school_inventory TO school_admin;
\q
```

3. **Clonar y configurar proyecto**
```bash
cd /var/www
sudo git clone tu-repositorio school_inventory
cd school_inventory
sudo python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Configurar .env**
```bash
cp .env.example .env
nano .env
# Editar con tus valores
```

5. **Ejecutar migraciones**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

6. **Configurar Gunicorn**
```bash
sudo nano /etc/systemd/system/school_inventory.service
```

Contenido:
```ini
[Unit]
Description=School Inventory Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/school_inventory
Environment="PATH=/var/www/school_inventory/venv/bin"
ExecStart=/var/www/school_inventory/venv/bin/gunicorn --workers 3 --bind unix:/var/www/school_inventory/school_inventory.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start school_inventory
sudo systemctl enable school_inventory
```

7. **Configurar Nginx**
```bash
sudo nano /etc/nginx/sites-available/school_inventory
```

Contenido:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/school_inventory;
    }
    
    location /media/ {
        root /var/www/school_inventory;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/school_inventory/school_inventory.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/school_inventory /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

---

## Post-Despliegue

### Crear datos de prueba
```bash
python manage.py shell < create_sample_data.py
```

### Backup de Base de Datos
```bash
# PostgreSQL
pg_dump school_inventory > backup_$(date +%Y%m%d).sql

# Restaurar
psql school_inventory < backup_20240101.sql
```

### Actualizaciones
```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart school_inventory
```

---

## Monitoreo

### Ver logs
```bash
# Gunicorn
sudo journalctl -u school_inventory -f

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### Rendimiento
- Configurar más workers de Gunicorn según CPU
- Activar Redis para caché
- Configurar CDN para archivos estáticos
