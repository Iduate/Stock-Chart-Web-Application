from django.core.management.base import BaseCommand
from django.utils import timezone
from charts.models import ChartPrediction
from market_data.services import MarketDataService
from django.db.models import Q, Avg
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update predictions that have reached their target date and calculate accuracy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all pending predictions regardless of target date',
        )

    def handle(self, *args, **options):
        # Get current time
        now = timezone.now()
        
        # Find predictions that are pending and have reached their target date
        query = Q(status='pending')
        if not options['force']:
            query &= Q(target_date__lte=now)  # Target date has passed
            
        pending_predictions = ChartPrediction.objects.filter(query)
        
        self.stdout.write(f'Found {pending_predictions.count()} predictions to update')
        
        # Initialize market data service
        market_service = MarketDataService()
        
        updated_count = 0
        error_count = 0
        
        for prediction in pending_predictions:
            try:
                self.stdout.write(f'Processing prediction #{prediction.id} for {prediction.stock.symbol}')
                
                # Get the latest market data for this stock
                quote_data = market_service.get_real_time_quote(
                    prediction.stock.symbol,
                    market=prediction.stock.market.market_type
                )
                
                if quote_data and 'price' in quote_data:
                    # Update the prediction with actual price
                    prediction.actual_price = Decimal(str(quote_data['price']))
                    prediction.status = 'completed'
                    
                    # Calculate accuracy and profit
                    accuracy = prediction.calculate_accuracy()
                    profit = prediction.calculate_profit_rate()
                    
                    prediction.save()
                    
                    # Update the user's overall prediction accuracy
                    self.update_user_accuracy(prediction.user)
                    
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'✅ Updated prediction #{prediction.id}: '
                        f'${prediction.predicted_price} vs ${prediction.actual_price} '
                        f'(Accuracy: {accuracy}%, Profit: {profit}%)'
                    ))
                    
                else:
                    error_count += 1
                    self.stdout.write(self.style.WARNING(
                        f'⚠️ No market data available for {prediction.stock.symbol} '
                        f'(Market: {prediction.stock.market.market_type})'
                    ))
                    
            except Exception as e:
                error_count += 1
                logger.error(f'Error processing prediction {prediction.id}: {e}')
                self.stdout.write(self.style.ERROR(
                    f'❌ Error processing prediction #{prediction.id}: {str(e)}'
                ))
                
        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Update Summary:'
            f'\n   ✅ Successfully updated: {updated_count} predictions'
            f'\n   ❌ Errors encountered: {error_count} predictions'
            f'\n   📈 Total processed: {updated_count + error_count} predictions'
        ))

    def update_user_accuracy(self, user):
        """Update user's overall prediction accuracy"""
        try:
            user_predictions = ChartPrediction.objects.filter(
                user=user,
                status='completed',
                accuracy_percentage__isnull=False
            )
            
            if user_predictions.exists():
                avg_accuracy = user_predictions.aggregate(
                    avg_accuracy=Avg('accuracy_percentage')
                )['avg_accuracy']
                
                avg_profit = user_predictions.aggregate(
                    avg_profit=Avg('profit_rate')
                )['avg_profit']
                
                user.prediction_accuracy = avg_accuracy or 0
                user.total_profit = avg_profit or 0
                user.save(update_fields=['prediction_accuracy', 'total_profit'])
                
                self.stdout.write(
                    f'   📊 Updated {user.username}: '
                    f'Accuracy {avg_accuracy:.1f}%, Profit {avg_profit:.1f}%'
                )
        except Exception as e:
            logger.error(f'Error updating user accuracy for {user.username}: {e}')
            self.stdout.write(self.style.WARNING(
                f'   ⚠️ Failed to update accuracy for user {user.username}'
            ))
