"""
Shipping Service for NitePutter Pro
Handles shipping calculations, tracking, and carrier integrations
"""

import os
import requests
import asyncio
from typing import Dict, List, Optional, Any
from decimal import Decimal
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ShippingService:
    def __init__(self):
        self.usps_user_id = os.getenv('USPS_USER_ID')
        self.ups_api_key = os.getenv('UPS_API_KEY')
        self.fedex_api_key = os.getenv('FEDEX_API_KEY')
        
        # Default shipping rates (fallback if APIs unavailable)
        self.default_rates = {
            'standard': {'rate': 9.99, 'days': '5-7 business days'},
            'expedited': {'rate': 19.99, 'days': '2-3 business days'},
            'overnight': {'rate': 39.99, 'days': '1 business day'}
        }
        
        # Product weights (in lbs) for NitePutter Pro products
        self.product_weights = {
            'basic_putter_light': 0.5,
            'pro_putter_system': 1.2,
            'complete_kit': 2.8,
            'charging_cable': 0.1,
            'mounting_kit': 0.3,
            'carrying_case': 0.4
        }
    
    async def calculate_shipping_cost(
        self, 
        items: List[Dict[str, Any]], 
        destination_zip: str,
        shipping_method: str = 'standard'
    ) -> Dict[str, Any]:
        """Calculate shipping cost for order items"""
        
        try:
            # Calculate total weight
            total_weight = self._calculate_total_weight(items)
            
            # Get origin ZIP (Heath, TX)
            origin_zip = "75032"
            
            # Try to get live rates from USPS first
            if self.usps_user_id:
                usps_rates = await self._get_usps_rates(
                    origin_zip, destination_zip, total_weight
                )
                if usps_rates:
                    return usps_rates
            
            # Fallback to calculated rates
            return self._calculate_fallback_rates(
                total_weight, destination_zip, shipping_method
            )
            
        except Exception as e:
            logger.error(f"Error calculating shipping: {str(e)}")
            return self._get_default_shipping(shipping_method)
    
    def _calculate_total_weight(self, items: List[Dict[str, Any]]) -> float:
        """Calculate total weight of order items"""
        total_weight = 0.0
        
        for item in items:
            product_id = item.get('id', '').lower()
            quantity = item.get('quantity', 1)
            
            # Map product IDs to weights
            weight = 0.5  # default weight
            
            if 'basic' in product_id or 'lite' in product_id:
                weight = self.product_weights['basic_putter_light']
            elif 'pro' in product_id:
                weight = self.product_weights['pro_putter_system']
            elif 'complete' in product_id or 'kit' in product_id:
                weight = self.product_weights['complete_kit']
            elif 'cable' in product_id:
                weight = self.product_weights['charging_cable']
            elif 'mount' in product_id:
                weight = self.product_weights['mounting_kit']
            elif 'case' in product_id:
                weight = self.product_weights['carrying_case']
            
            total_weight += weight * quantity
        
        # Minimum weight for shipping calculation
        return max(total_weight, 0.5)
    
    async def _get_usps_rates(
        self, 
        origin_zip: str, 
        destination_zip: str, 
        weight_lbs: float
    ) -> Optional[Dict[str, Any]]:
        """Get live shipping rates from USPS API"""
        
        if not self.usps_user_id:
            return None
            
        try:
            # Convert weight to ounces (USPS uses ounces)
            weight_oz = max(int(weight_lbs * 16), 1)
            
            # USPS Rate Calculator API
            xml_request = f'''
            <RateV4Request USERID="{self.usps_user_id}">
                <Revision>2</Revision>
                <Package ID="1ST">
                    <Service>PRIORITY</Service>
                    <ZipOrigination>{origin_zip}</ZipOrigination>
                    <ZipDestination>{destination_zip}</ZipDestination>
                    <Pounds>{int(weight_lbs)}</Pounds>
                    <Ounces>{weight_oz % 16}</Ounces>
                    <Container>VARIABLE</Container>
                    <Size>REGULAR</Size>
                    <Machinable>TRUE</Machinable>
                </Package>
            </RateV4Request>
            '''
            
            response = requests.get(
                'https://secure.shippingapis.com/ShippingAPI.dll',
                params={
                    'API': 'RateV4',
                    'XML': xml_request
                },
                timeout=10
            )
            
            if response.status_code == 200:
                # Parse USPS XML response (simplified)
                # In production, use proper XML parsing
                if 'Rate' in response.text and 'Error' not in response.text:
                    # Extract rate from XML (this is simplified)
                    import re
                    rate_match = re.search(r'<Rate>([\d.]+)</Rate>', response.text)
                    if rate_match:
                        priority_rate = float(rate_match.group(1))
                        
                        return {
                            'rates': {
                                'standard': {
                                    'rate': priority_rate + 2.00,  # Ground equivalent
                                    'days': '5-7 business days',
                                    'service': 'USPS Ground'
                                },
                                'expedited': {
                                    'rate': priority_rate,
                                    'days': '2-3 business days', 
                                    'service': 'USPS Priority Mail'
                                },
                                'overnight': {
                                    'rate': priority_rate * 2.5,
                                    'days': '1 business day',
                                    'service': 'USPS Priority Express'
                                }
                            },
                            'source': 'usps_api'
                        }
        
        except Exception as e:
            logger.error(f"USPS API error: {str(e)}")
            return None
        
        return None
    
    def _calculate_fallback_rates(
        self, 
        weight_lbs: float, 
        destination_zip: str, 
        preferred_method: str
    ) -> Dict[str, Any]:
        """Calculate shipping rates using distance-based pricing"""
        
        try:
            # Determine shipping zone based on ZIP code
            zone = self._get_shipping_zone(destination_zip)
            
            # Base rates by zone
            zone_multipliers = {
                1: 1.0,    # Local (Texas, nearby states)
                2: 1.2,    # Regional (surrounding states)
                3: 1.4,    # National (most of US)
                4: 1.6,    # Far (Alaska, Hawaii, territories)
            }
            
            multiplier = zone_multipliers.get(zone, 1.2)
            
            # Weight-based pricing
            weight_factor = 1.0 + (max(weight_lbs - 1, 0) * 0.3)
            
            rates = {}
            for method, base_info in self.default_rates.items():
                adjusted_rate = base_info['rate'] * multiplier * weight_factor
                rates[method] = {
                    'rate': round(adjusted_rate, 2),
                    'days': base_info['days'],
                    'service': f'NitePutter {method.title()} Shipping'
                }
            
            return {
                'rates': rates,
                'zone': zone,
                'weight': weight_lbs,
                'source': 'calculated'
            }
            
        except Exception as e:
            logger.error(f"Fallback rate calculation error: {str(e)}")
            return self._get_default_shipping(preferred_method)
    
    def _get_shipping_zone(self, destination_zip: str) -> int:
        """Determine shipping zone based on destination ZIP code"""
        
        if not destination_zip or len(destination_zip) < 5:
            return 3  # Default to national
        
        zip_prefix = destination_zip[:3]
        
        # Zone 1: Texas and nearby states (750-799)
        if zip_prefix in ['750', '751', '752', '753', '754', '755', '756', '757', '758', '759',
                         '760', '761', '762', '763', '764', '765', '766', '767', '768', '769',
                         '770', '771', '772', '773', '774', '775', '776', '777', '778', '779',
                         '780', '781', '782', '783', '784', '785', '786', '787', '788', '789',
                         '790', '791', '792', '793', '794', '795', '796', '797', '798', '799']:
            return 1
        
        # Zone 2: Regional states
        if zip_prefix in ['630', '631', '632', '633', '634', '635', '636', '637', '638', '639',
                         '640', '641', '642', '643', '644', '645', '646', '647', '648', '649',
                         '650', '651', '652', '653', '654', '655', '656', '657', '658', '659',
                         '660', '661', '662', '663', '664', '665', '666', '667', '668', '669']:
            return 2
        
        # Zone 4: Alaska, Hawaii, territories
        if zip_prefix in ['995', '996', '997', '998', '999'] or destination_zip.startswith('96'):
            return 4
        
        # Zone 3: Everything else (most of continental US)
        return 3
    
    def _get_default_shipping(self, method: str = 'standard') -> Dict[str, Any]:
        """Get default shipping rate when all else fails"""
        
        selected_rate = self.default_rates.get(method, self.default_rates['standard'])
        
        return {
            'rates': {
                method: {
                    'rate': selected_rate['rate'],
                    'days': selected_rate['days'],
                    'service': f'NitePutter {method.title()} Shipping'
                }
            },
            'source': 'default'
        }
    
    async def get_tracking_info(self, tracking_number: str, carrier: str = 'usps') -> Dict[str, Any]:
        """Get tracking information for shipped package"""
        
        try:
            if carrier.lower() == 'usps':
                return await self._get_usps_tracking(tracking_number)
            elif carrier.lower() == 'ups':
                return await self._get_ups_tracking(tracking_number)
            elif carrier.lower() == 'fedex':
                return await self._get_fedex_tracking(tracking_number)
            else:
                return self._get_generic_tracking_info(tracking_number, carrier)
                
        except Exception as e:
            logger.error(f"Tracking lookup error: {str(e)}")
            return {
                'tracking_number': tracking_number,
                'status': 'Information Not Available',
                'error': 'Unable to retrieve tracking information at this time'
            }
    
    async def _get_usps_tracking(self, tracking_number: str) -> Dict[str, Any]:
        """Get USPS tracking information"""
        
        if not self.usps_user_id:
            return self._get_generic_tracking_info(tracking_number, 'USPS')
        
        try:
            xml_request = f'''
            <TrackRequest USERID="{self.usps_user_id}">
                <TrackID ID="{tracking_number}"></TrackID>
            </TrackRequest>
            '''
            
            response = requests.get(
                'https://secure.shippingapis.com/ShippingAPI.dll',
                params={
                    'API': 'TrackV2',
                    'XML': xml_request
                },
                timeout=10
            )
            
            if response.status_code == 200 and 'Error' not in response.text:
                # Parse tracking info (simplified)
                return {
                    'tracking_number': tracking_number,
                    'status': 'In Transit',
                    'estimated_delivery': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                    'carrier': 'USPS',
                    'tracking_url': f'https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}',
                    'last_update': datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"USPS tracking error: {str(e)}")
        
        return self._get_generic_tracking_info(tracking_number, 'USPS')
    
    async def _get_ups_tracking(self, tracking_number: str) -> Dict[str, Any]:
        """Get UPS tracking information"""
        # UPS API integration would go here
        return self._get_generic_tracking_info(tracking_number, 'UPS')
    
    async def _get_fedex_tracking(self, tracking_number: str) -> Dict[str, Any]:
        """Get FedEx tracking information"""
        # FedEx API integration would go here
        return self._get_generic_tracking_info(tracking_number, 'FedEx')
    
    def _get_generic_tracking_info(self, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """Return generic tracking info when APIs are unavailable"""
        
        tracking_urls = {
            'USPS': f'https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}',
            'UPS': f'https://www.ups.com/track?loc=en_US&tracknum={tracking_number}',
            'FedEx': f'https://www.fedex.com/apps/fedextrack/?tracknumber={tracking_number}'
        }
        
        return {
            'tracking_number': tracking_number,
            'status': 'Shipped - Track Online',
            'carrier': carrier,
            'tracking_url': tracking_urls.get(carrier, '#'),
            'estimated_delivery': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'message': f'Please visit {carrier} website for detailed tracking information',
            'last_update': datetime.now().isoformat()
        }
    
    def get_shipping_methods(self) -> List[Dict[str, Any]]:
        """Get available shipping methods"""
        
        return [
            {
                'id': 'standard',
                'name': 'Standard Shipping',
                'description': '5-7 business days',
                'base_rate': self.default_rates['standard']['rate']
            },
            {
                'id': 'expedited', 
                'name': 'Expedited Shipping',
                'description': '2-3 business days',
                'base_rate': self.default_rates['expedited']['rate']
            },
            {
                'id': 'overnight',
                'name': 'Overnight Shipping', 
                'description': 'Next business day',
                'base_rate': self.default_rates['overnight']['rate']
            }
        ]

# Global shipping service instance
shipping_service = ShippingService()