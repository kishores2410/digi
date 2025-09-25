"""
24DIGI Data Manager
Handles all data operations, pricing configurations, and input management
"""

import streamlit as st
import pandas as pd
import json
from typing import Dict, Any, List
from config.app_config import AppConfig

class DataManager:
    """Manages all application data and configurations"""
    
    def __init__(self):
        """Initialize the data manager"""
        self.pricing_data = AppConfig.DEFAULT_PRICING.copy()
        self.inputs = AppConfig.DEFAULT_INPUTS.copy()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'pricing_data' not in st.session_state:
            st.session_state.pricing_data = self.pricing_data
        else:
            self.pricing_data = st.session_state.pricing_data
        
        if 'input_data' not in st.session_state:
            st.session_state.input_data = self.inputs
        else:
            self.inputs = st.session_state.input_data
    
    def get_pricing_data(self, subscription_type: str = None) -> Dict:
        """Get pricing data for a specific subscription type or all"""
        if subscription_type:
            return self.pricing_data.get(subscription_type, {})
        return self.pricing_data
    
    def update_pricing_data(self, subscription_type: str, pricing_updates: Dict):
        """Update pricing data for a subscription type"""
        if subscription_type in self.pricing_data:
            self.pricing_data[subscription_type].update(pricing_updates)
            st.session_state.pricing_data = self.pricing_data
    
    def get_input_data(self) -> Dict:
        """Get current input data"""
        return self.inputs
    
    def update_input_data(self, updates: Dict):
        """Update input data"""
        self.inputs.update(updates)
        st.session_state.input_data = self.inputs
    
    def reset_pricing_to_defaults(self):
        """Reset pricing data to default values"""
        self.pricing_data = AppConfig.DEFAULT_PRICING.copy()
        st.session_state.pricing_data = self.pricing_data
    
    def export_pricing_config(self) -> str:
        """Export pricing configuration as JSON string"""
        return json.dumps(self.pricing_data, indent=2)
    
    def import_pricing_config(self, config_json: str) -> bool:
        """Import pricing configuration from JSON string"""
        try:
            pricing_data = json.loads(config_json)
            # Validate the structure
            if self._validate_pricing_structure(pricing_data):
                self.pricing_data = pricing_data
                st.session_state.pricing_data = self.pricing_data
                return True
        except json.JSONDecodeError:
            pass
        return False
    
    def _validate_pricing_structure(self, data: Dict) -> bool:
        """Validate pricing data structure"""
        required_types = ['VIP', 'Normal', 'Custom']
        for sub_type in required_types:
            if sub_type not in data:
                return False
        return True
    
    def get_subscription_combinations(self) -> List[Dict]:
        """Get all subscription type and duration combinations"""
        combinations = []
        for sub_type in AppConfig.SUBSCRIPTION_TYPES:
            for duration in AppConfig.SUBSCRIPTION_DURATIONS:
                key = f"{sub_type}_{duration}_month{'s' if duration > 1 else ''}"
                combinations.append({
                    'type': sub_type,
                    'duration': duration,
                    'key': key,
                    'display_name': f"{sub_type} - {duration} Month{'s' if duration > 1 else ''}"
                })
        return combinations
    
    def calculate_package_cost(self, subscription_type: str, duration: int) -> Dict:
        """Calculate the total cost/revenue for a subscription package"""
        pricing = self.pricing_data.get(subscription_type, {})
        
        if duration == 1:
            package_cost = (
                pricing.get('mealsPerMonth', {}).get('cost', 0) +
                pricing.get('deliveryPerMonth', {}).get('cost', 0) +
                pricing.get('bracelet', {}).get('cost', 0) +
                pricing.get('pointsX10', {}).get('cost', 0)
            )
            package_revenue = (
                pricing.get('mealsPerMonth', {}).get('selling', 0) +
                pricing.get('deliveryPerMonth', {}).get('selling', 0) +
                pricing.get('bracelet', {}).get('selling', 0) +
                pricing.get('pointsX10', {}).get('selling', 0)
            )
        else:  # 3 months
            package_cost = (
                pricing.get('meals3Months', {}).get('cost', 0) +
                pricing.get('delivery3Months', {}).get('cost', 0) +
                pricing.get('bracelet', {}).get('cost', 0) +
                pricing.get('pointsX10', {}).get('cost', 0)
            )
            package_revenue = (
                pricing.get('meals3Months', {}).get('selling', 0) +
                pricing.get('delivery3Months', {}).get('selling', 0) +
                pricing.get('bracelet', {}).get('selling', 0) +
                pricing.get('pointsX10', {}).get('selling', 0)
            )
        
        # Add digital profit for non-Custom subscriptions
        if subscription_type != 'Custom':
            package_revenue += pricing.get('digitalProfit', 0)
        
        return {
            'cost': package_cost,
            'revenue': package_revenue,
            'profit': package_revenue - package_cost
        }
    
    def get_summary_dataframe(self) -> pd.DataFrame:
        """Create a summary DataFrame of all subscription packages"""
        data = []
        for combo in self.get_subscription_combinations():
            package_data = self.calculate_package_cost(combo['type'], combo['duration'])
            customers = self.inputs.get(f"{combo['type']}_{combo['duration']}_month{'s' if combo['duration'] > 1 else ''}", {}).get('customers', 0)
            renewals = self.inputs.get(f"{combo['type']}_{combo['duration']}_month{'s' if combo['duration'] > 1 else ''}", {}).get('renewals', 0)
            
            total_cost = package_data['cost'] * customers
            total_revenue = package_data['revenue'] * customers
            renewal_revenue = renewals * (1500 if combo['duration'] == 1 else 4500)
            
            data.append({
                'Subscription Type': combo['type'],
                'Duration (Months)': combo['duration'],
                'Customers': customers,
                'Cost per Customer': package_data['cost'],
                'Revenue per Customer': package_data['revenue'],
                'Total Cost': total_cost,
                'Total Revenue': total_revenue + renewal_revenue,
                'Total Profit': (total_revenue + renewal_revenue) - total_cost,
                'Profit Margin (%)': ((total_revenue + renewal_revenue) - total_cost) / (total_revenue + renewal_revenue) * 100 if total_revenue > 0 else 0,
                'Renewals': renewals,
                'Renewal Revenue': renewal_revenue
            })
        
        return pd.DataFrame(data)
    
    def get_additional_services_summary(self) -> Dict:
        """Calculate summary for additional services"""
        pricing = self.pricing_data
        
        # Events & Challenges
        challenge_revenue = self.inputs.get('challenge_fee', 25) * self.inputs.get('challenge_participants', 200)
        adventure_revenue = self.inputs.get('adventure_fee', 40) * self.inputs.get('adventure_participants', 150)
        competition_revenue = self.inputs.get('competition_fee', 35) * self.inputs.get('competition_participants', 100)
        events_total = challenge_revenue + adventure_revenue + competition_revenue
        
        # Additional Bracelets (assuming VIP pricing)
        additional_bracelets = self.inputs.get('additional_bracelets', 100)
        bracelet_cost = pricing['VIP']['bracelet']['cost'] * additional_bracelets
        bracelet_revenue = pricing['VIP']['bracelet']['selling'] * additional_bracelets
        
        # CBYI Services (Custom pricing)
        cbyi_customers = self.inputs.get('cbyi_non_subscribers', 50)
        cbyi_cost = pricing['Custom']['cbyiOneMonth']['cost'] * cbyi_customers
        cbyi_revenue = pricing['Custom']['cbyiOneMonth']['selling'] * cbyi_customers
        
        # Non-subscriber Bracelets
        ns_bracelets = self.inputs.get('bracelets_non_subscribers', 75)
        ns_bracelet_cost = pricing['VIP']['bracelet']['cost'] * ns_bracelets
        ns_bracelet_revenue = pricing['VIP']['bracelet']['selling'] * ns_bracelets
        
        # Car Rental
        car_customers = self.inputs.get('car_rental_customers', 20)
        car_cost = pricing['VIP']['carOneMonth']['cost'] * car_customers
        car_revenue = pricing['VIP']['carOneMonth']['selling'] * car_customers
        
        return {
            'Events & Challenges': {
                'cost': 0,
                'revenue': events_total,
                'profit': events_total
            },
            'Additional Bracelets': {
                'cost': bracelet_cost,
                'revenue': bracelet_revenue,
                'profit': bracelet_revenue - bracelet_cost
            },
            'CBYI Services': {
                'cost': cbyi_cost,
                'revenue': cbyi_revenue,
                'profit': cbyi_revenue - cbyi_cost
            },
            'Non-Subscriber Bracelets': {
                'cost': ns_bracelet_cost,
                'revenue': ns_bracelet_revenue,
                'profit': ns_bracelet_revenue - ns_bracelet_cost
            },
            'Car Rental': {
                'cost': car_cost,
                'revenue': car_revenue,
                'profit': car_revenue - car_cost
            }
        }
