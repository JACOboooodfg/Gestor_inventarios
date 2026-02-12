from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Article, Loan, Alert, Movement
from django.utils import timezone


@receiver(post_save, sender=Article)
def check_low_stock(sender, instance, created, **kwargs):
    """Crear alerta cuando el stock está bajo"""
    if instance.is_low_stock and instance.status == 'available':
        # Verificar si ya existe una alerta no leída
        existing_alert = Alert.objects.filter(
            article=instance,
            alert_type='low_stock',
            is_read=False
        ).first()
        
        if not existing_alert:
            Alert.objects.create(
                alert_type='low_stock',
                article=instance,
                message=f"Stock bajo para {instance.name}. Cantidad actual: {instance.quantity} {instance.unit}. Mínimo requerido: {instance.min_quantity} {instance.unit}."
            )


@receiver(post_save, sender=Loan)
def check_overdue_loan(sender, instance, created, **kwargs):
    """Crear alerta cuando un préstamo está vencido"""
    if instance.is_overdue and instance.status == 'active':
        # Verificar si ya existe una alerta no leída
        existing_alert = Alert.objects.filter(
            loan=instance,
            alert_type='overdue_loan',
            is_read=False
        ).first()
        
        if not existing_alert:
            Alert.objects.create(
                alert_type='overdue_loan',
                loan=instance,
                article=instance.article,
                message=f"Préstamo vencido: {instance.article.name} prestado a {instance.borrower_name}. Vencido hace {instance.days_overdue} días."
            )


@receiver(pre_save, sender=Article)
def track_quantity_change(sender, instance, **kwargs):
    """Registrar cambios de cantidad automáticamente"""
    if instance.pk:
        try:
            old_instance = Article.objects.get(pk=instance.pk)
            if old_instance.quantity != instance.quantity:
                # Se registrará en el save de la vista
                pass
        except Article.DoesNotExist:
            pass
