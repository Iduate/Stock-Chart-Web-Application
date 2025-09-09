from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from charts.models import ChartPrediction
from users.models import User
from django.db.models import Avg
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=ChartPrediction)
def auto_publish_prediction(sender, instance, **kwargs):
    """
    Automatically publish predictions to the public board when created
    """
    if not instance.pk:  # New prediction
        # Always set to public unless user explicitly sets otherwise
        if instance.is_public is None:
            instance.is_public = True
        
        # Set prediction date to now if not set
        if not instance.prediction_date:
            instance.prediction_date = timezone.now()
        
        logger.info(f'New prediction created for {instance.stock.symbol} by {instance.user.username}')

@receiver(post_save, sender=ChartPrediction)
def update_user_stats_on_completion(sender, instance, created, **kwargs):
    """
    Update user statistics when a prediction is completed
    """
    if instance.status == 'completed' and instance.accuracy_percentage is not None:
        try:
            user = instance.user
            
            # Recalculate user's overall accuracy
            completed_predictions = ChartPrediction.objects.filter(
                user=user,
                status='completed',
                accuracy_percentage__isnull=False
            )
            
            if completed_predictions.exists():
                avg_accuracy = completed_predictions.aggregate(
                    avg_accuracy=Avg('accuracy_percentage')
                )['avg_accuracy']
                
                avg_profit = completed_predictions.aggregate(
                    avg_profit=Avg('profit_rate')
                )['avg_profit']
                
                # Update user stats
                user.prediction_accuracy = avg_accuracy or 0
                user.total_profit = avg_profit or 0
                user.save(update_fields=['prediction_accuracy', 'total_profit'])
                
                logger.info(
                    f'Updated stats for {user.username}: '
                    f'Accuracy {avg_accuracy:.1f}%, Profit {avg_profit:.1f}%'
                )
        except Exception as e:
            logger.error(f'Error updating user stats: {e}')

@receiver(post_save, sender=ChartPrediction)
def log_prediction_activity(sender, instance, created, **kwargs):
    """
    Log prediction activity for monitoring and analytics
    """
    if created:
        logger.info(
            f'📊 New prediction: {instance.user.username} predicts '
            f'{instance.stock.symbol} will be ${instance.predicted_price} '
            f'by {instance.target_date} (currently ${instance.current_price})'
        )
    elif instance.status == 'completed':
        accuracy = instance.accuracy_percentage or 0
        profit = instance.profit_rate or 0
        logger.info(
            f'✅ Prediction completed: {instance.user.username} '
            f'predicted ${instance.predicted_price} vs actual ${instance.actual_price} '
            f'(Accuracy: {accuracy:.1f}%, Profit: {profit:.1f}%)'
        )
