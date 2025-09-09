"""
PayPal utilities for the payment system
"""
import json
import requests
from django.conf import settings
import base64
import logging

logger = logging.getLogger(__name__)

def get_paypal_access_token():
    """
    Get an access token from PayPal API
    
    Returns:
        str: Access token or None if failed
    """
    try:
        # Create auth string
        auth = base64.b64encode(
            f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}".encode()
        ).decode()
        
        # Set up headers
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        # Make the request
        response = requests.post(
            'https://api-m.sandbox.paypal.com/v1/oauth2/token',
            headers=headers,
            data='grant_type=client_credentials'
        )
        
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            logger.error(f"Failed to get PayPal token: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error getting PayPal token: {e}")
        return None
        
def create_paypal_order(plan, currency='USD'):
    """
    Create a PayPal order for a subscription plan
    
    Args:
        plan: The PaymentPlan model instance
        currency: The currency code (default: USD)
        
    Returns:
        dict: Order details with ID and approval URL or None if failed
    """
    try:
        access_token = get_paypal_access_token()
        if not access_token:
            return None
            
        # Get the price based on currency
        price = str(plan.price_usd) if currency == 'USD' else str(plan.price_krw)
        
        # Set up headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        # Create order payload
        payload = {
            'intent': 'CAPTURE',
            'purchase_units': [
                {
                    'reference_id': f'plan_{plan.id}',
                    'description': f'StockChart Premium: {plan.name}',
                    'amount': {
                        'currency_code': currency,
                        'value': price
                    }
                }
            ],
            'application_context': {
                'brand_name': 'StockChart',
                'landing_page': 'LOGIN',
                'user_action': 'PAY_NOW',
                'return_url': 'https://stockchart.kr/payment/success',
                'cancel_url': 'https://stockchart.kr/payment/cancel'
            }
        }
        
        # Make the request
        response = requests.post(
            'https://api-m.sandbox.paypal.com/v2/checkout/orders',
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code in (200, 201):
            data = response.json()
            
            # Extract approval URL
            approval_url = next(
                link['href'] for link in data['links'] 
                if link['rel'] == 'approve'
            )
            
            return {
                'id': data['id'],
                'status': data['status'],
                'approval_url': approval_url
            }
        else:
            logger.error(f"Failed to create PayPal order: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error creating PayPal order: {e}")
        return None
        
def capture_paypal_order(order_id):
    """
    Capture an approved PayPal order to complete the payment
    
    Args:
        order_id: The PayPal order ID to capture
        
    Returns:
        dict: Capture details or None if failed
    """
    try:
        access_token = get_paypal_access_token()
        if not access_token:
            return None
            
        # Set up headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        # Make the request
        response = requests.post(
            f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture',
            headers=headers
        )
        
        if response.status_code in (200, 201):
            return response.json()
        else:
            logger.error(f"Failed to capture PayPal order: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error capturing PayPal order: {e}")
        return None
