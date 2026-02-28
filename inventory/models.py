from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class Category(models.Model):
    """Categorías de artículos (Ciencias, Deportes, Tecnología, etc.)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    icon = models.CharField(max_length=50, blank=True, help_text="Nombre de icono (opcional)", verbose_name="Ícono")
    color = models.CharField(max_length=7, default="#3B82F6", help_text="Color en hexadecimal", verbose_name="Color")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_items(self):
        """Total de artículos en esta categoría"""
        return self.articles.count()
    
    @property
    def total_quantity(self):
        """Cantidad total de unidades en esta categoría"""
        return sum(article.quantity for article in self.articles.all())
    
    @property
    def total_value(self):
        """Valor total del inventario en esta categoría"""
        return sum(article.total_value for article in self.articles.all() if article.total_value)


class Location(models.Model):
    """Ubicaciones físicas donde se almacenan los artículos"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    building = models.CharField(max_length=100, blank=True, verbose_name="Edificio")
    floor = models.CharField(max_length=50, blank=True, verbose_name="Piso")
    room = models.CharField(max_length=50, blank=True, verbose_name="Salón/Aula")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    
    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        ordering = ['building', 'floor', 'room']
    
    def __str__(self):
        parts = [self.name]
        if self.building:
            parts.append(f"Edificio {self.building}")
        if self.floor:
            parts.append(f"Piso {self.floor}")
        if self.room:
            parts.append(f"Salón {self.room}")
        return " - ".join(parts)


class Article(models.Model):
    """Artículos del inventario"""
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('in_use', 'En uso'),
        ('maintenance', 'En mantenimiento'),
        ('damaged', 'Dañado'),
        ('retired', 'Dado de baja'),
    ]
    
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='articles', verbose_name="Categoría")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles', verbose_name="Ubicación")
    quantity = models.IntegerField(validators=[MinValueValidator(0)], default=0, verbose_name="Cantidad")
    min_quantity = models.IntegerField(validators=[MinValueValidator(0)], default=5, verbose_name="Cantidad mínima", help_text="Alerta cuando esté por debajo")
    unit = models.CharField(max_length=50, default="unidad", verbose_name="Unidad de medida")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Estado")
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name="Imagen")
    barcode = models.CharField(max_length=100, blank=True, verbose_name="Código de barras")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio unitario")
    
    # 📅 FECHA DE COMPRA (CORREGIDO - EN LUGAR CORRECTO)
    purchase_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Fecha de Compra',
        help_text='Fecha en que se adquirió el artículo'
    )
    
    # 🏪 PROVEEDOR/LUGAR DE COMPRA (NUEVO)
    supplier = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Proveedor',
        help_text='Lugar o proveedor donde se compró el artículo'
    )
    
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles_created', verbose_name="Creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_low_stock(self):
        """Verifica si el stock está bajo"""
        return self.quantity <= self.min_quantity
    
    @property
    def total_value(self):
        """Valor total del inventario de este artículo"""
        if self.price:
            return self.quantity * self.price
        return 0
    
    def save(self, *args, **kwargs):
        if not self.code:
            # Generar código automático si no existe
            last_article = Article.objects.all().order_by('id').last()
            if last_article:
                self.code = f"ART-{last_article.id + 1:05d}"
            else:
                self.code = "ART-00001"
        super().save(*args, **kwargs)


class Movement(models.Model):
    """Registro de movimientos de inventario (entradas, salidas, ajustes)"""
    TYPE_CHOICES = [
        ('entry', 'Entrada'),
        ('exit', 'Salida'),
        ('adjustment', 'Ajuste'),
        ('transfer', 'Transferencia'),
        ('loan', 'Préstamo'),
        ('return', 'Devolución'),
    ]
    
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='movements', verbose_name="Artículo")
    movement_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo de movimiento")
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Cantidad")
    previous_quantity = models.IntegerField(verbose_name="Cantidad anterior")
    new_quantity = models.IntegerField(verbose_name="Cantidad nueva")
    reason = models.TextField(verbose_name="Motivo/Razón")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Referencia", help_text="Número de factura, orden, etc.")
    from_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_from', verbose_name="Desde ubicación")
    to_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_to', verbose_name="Hacia ubicación")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuario")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    
    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.article.name} - {self.quantity} {self.article.unit}"


class Loan(models.Model):
    """Sistema de préstamos de artículos"""
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('returned', 'Devuelto'),
        ('overdue', 'Vencido'),
        ('cancelled', 'Cancelado'),
    ]
    
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='loans', verbose_name="Artículo")
    borrower_name = models.CharField(max_length=200, verbose_name="Nombre del solicitante")
    borrower_id = models.CharField(max_length=50, blank=True, verbose_name="ID/Matrícula")
    borrower_contact = models.CharField(max_length=100, blank=True, verbose_name="Contacto")
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Cantidad")
    loan_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de préstamo")
    due_date = models.DateTimeField(verbose_name="Fecha de devolución")
    return_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de devolución real")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Estado")
    notes = models.TextField(blank=True, verbose_name="Notas")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='loans_approved', verbose_name="Aprobado por")
    returned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='loans_returned', verbose_name="Recibido por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    
    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-loan_date']
    
    def __str__(self):
        return f"{self.article.name} - {self.borrower_name}"
    
    @property
    def is_overdue(self):
        """Verifica si el préstamo está vencido"""
        if self.status == 'active' and self.due_date < timezone.now():
            return True
        return False
    
    @property
    def days_overdue(self):
        """Días de retraso"""
        if self.is_overdue:
            return (timezone.now() - self.due_date).days
        return 0
    
    def save(self, *args, **kwargs):
        # Actualizar estado automáticamente
        if self.return_date and self.status == 'active':
            self.status = 'returned'
        elif self.is_overdue and self.status == 'active':
            self.status = 'overdue'
        super().save(*args, **kwargs)


class Alert(models.Model):
    """Alertas del sistema (stock bajo, préstamos vencidos, etc.)"""
    TYPE_CHOICES = [
        ('low_stock', 'Stock bajo'),
        ('overdue_loan', 'Préstamo vencido'),
        ('maintenance', 'Mantenimiento requerido'),
        ('other', 'Otro'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo de alerta")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts', verbose_name="Artículo")
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts', verbose_name="Préstamo")
    message = models.TextField(verbose_name="Mensaje")
    is_read = models.BooleanField(default=False, verbose_name="Leída")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    read_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Leída por")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de lectura")
    
    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.message[:50]}"