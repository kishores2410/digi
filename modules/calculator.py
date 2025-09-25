"""
24DIGI Revenue Calculator
Handles all revenue and profit calculations
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from modules.data_manager import DataManager

class RevenueCalculator:
    """Comprehensive revenue calculator for all subscription combinations"""
    
    def __init__(self, data_manager: DataManager):
        """Initialize calculator with data manager"""
        self.data_manager = data_manager
    
    def calculate_comprehensive_results(self) -> Dict[str, Any]:
        """Calculate results for all subscription combinations and services"""
        results = {
            'subscriptions': {},
            'additional_services': {},
            'totals': {},
            'summary': {},
            'breakdown': []
        }
        
        # Calculate subscription results
        subscription_results = self._calculate_subscription_results()
        results['subscriptions'] = subscription_results
        
        # Calculate additional services
        additional_results = self._calculate_additional_services()
        results['additional_services'] = additional_results
        
        # Calculate totals
        results['totals'] = self._calculate_totals(subscription_results, additional_results)
        
        # Create summary
        results['summary'] = self._create_summary(results)
        
        # Create detailed breakdown
        results['breakdown'] = self._create_breakdown(subscription_results, additional_results)
        
        # Store in session state for sidebar access
        st.session_state.last_calculation = results['totals']
        
        return results
    
    def _calculate_subscription_results(self) -> Dict:
        """Calculate results for all subscription combinations"""
        subscription_results = {}
        combinations = self.data_manager.get_subscription_combinations()
        
        for combo in combinations:
            key = f"{combo['type']}_{combo['duration']}_month{'s' if combo['duration'] > 1 else ''}"
            customers = self.data_manager.inputs.get(key, {}).get('customers', 0)
            renewals = self.data_manager.inputs.get(key, {}).get('renewals', 0)
            
            if customers > 0:
                package_data = self.data_manager.calculate_package_cost(combo['type'], combo['duration'])
                
                # Calculate totals
                total_cost = package_data['cost'] * customers
                total_revenue = package_data['revenue'] * customers
                renewal_revenue = renewals * (1500 if combo['duration'] == 1 else 4500)
                
                subscription_results[combo['display_name']] = {
                    'type': combo['type'],
                    'duration': combo['duration'],
                    'customers': customers,
                    'renewals': renewals,
                    'cost_per_customer': package_data['cost'],
                    'revenue_per_customer': package_data['revenue'],
                    'total_cost': total_cost,
                    'total_revenue': total_revenue + renewal_revenue,
                    'total_profit': (total_revenue + renewal_revenue) - total_cost,
                    'profit_margin': ((total_revenue + renewal_revenue) - total_cost) / (total_revenue + renewal_revenue) * 100 if total_revenue > 0 else 0,
                    'renewal_revenue': renewal_revenue
                }
        
        return subscription_results
    
    def _calculate_additional_services(self) -> Dict:
        """Calculate results for additional services"""
        return self.data_manager.get_additional_services_summary()
    
    def _calculate_totals(self, subscription_results: Dict, additional_results: Dict) -> Dict:
        """Calculate overall totals"""
        total_cost = 0
        total_revenue = 0
        total_customers = 0
        
        # Sum subscription totals
        for sub_data in subscription_results.values():
            total_cost += sub_data['total_cost']
            total_revenue += sub_data['total_revenue']
            total_customers += sub_data['customers']
        
        # Sum additional services
        for service_data in additional_results.values():
            total_cost += service_data['cost']
            total_revenue += service_data['revenue']
        
        total_profit = total_revenue - total_cost
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'total_cost': total_cost,
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'profit_margin': profit_margin,
            'total_customers': total_customers,
            'revenue_per_customer': total_revenue / total_customers if total_customers > 0 else 0,
            'cost_per_customer': total_cost / total_customers if total_customers > 0 else 0,
            'profit_per_customer': total_profit / total_customers if total_customers > 0 else 0
        }
    
    def _create_summary(self, results: Dict) -> Dict:
        """Create executive summary"""
        totals = results['totals']
        subscription_count = len(results['subscriptions'])
        service_count = len(results['additional_services'])
        
        # Find best performing subscription
        best_subscription = max(
            results['subscriptions'].items(),
            key=lambda x: x[1]['total_profit'],
            default=('None', {'total_profit': 0})
        )
        
        return {
            'total_revenue': totals['total_revenue'],
            'total_profit': totals['total_profit'],
            'profit_margin': totals['profit_margin'],
            'total_customers': totals['total_customers'],
            'subscription_types_count': subscription_count,
            'additional_services_count': service_count,
            'best_subscription': best_subscription[0],
            'best_subscription_profit': best_subscription[1]['total_profit']
        }
    
    def _create_breakdown(self, subscription_results: Dict, additional_results: Dict) -> List[Dict]:
        """Create detailed breakdown for reporting"""
        breakdown = []
        
        # Add subscription breakdowns
        for name, data in subscription_results.items():
            breakdown.append({
                'category': 'Subscription',
                'name': name,
                'cost': data['total_cost'],
                'revenue': data['total_revenue'],
                'profit': data['total_profit'],
                'margin': data['profit_margin'],
                'customers': data['customers'],
                'details': f"{data['customers']} customers, {data['renewals']} renewals"
            })
        
        # Add additional service breakdowns
        for name, data in additional_results.items():
            breakdown.append({
                'category': 'Additional Service',
                'name': name,
                'cost': data['cost'],
                'revenue': data['revenue'],
                'profit': data['profit'],
                'margin': (data['profit'] / data['revenue'] * 100) if data['revenue'] > 0 else 0,
                'customers': 0,  # Not applicable for services
                'details': 'Additional service revenue'
            })
        
        return breakdown
    
    def calculate_growth_impact(self, growth_rate: float, periods: int = 12) -> Dict:
        """Calculate impact of growth rate over specified periods"""
        current_results = self.calculate_comprehensive_results()
        
        monthly_revenue = current_results['totals']['total_revenue'] / 3  # Assuming quarterly calculation
        monthly_cost = current_results['totals']['total_cost'] / 3
        monthly_profit = monthly_revenue - monthly_cost
        
        projected_data = []
        cumulative_revenue = 0
        cumulative_profit = 0
        
        for month in range(1, periods + 1):
            growth_factor = (1 + growth_rate) ** month
            projected_revenue = monthly_revenue * growth_factor
            projected_cost = monthly_cost * growth_factor
            projected_profit = projected_revenue - projected_cost
            
            cumulative_revenue += projected_revenue
            cumulative_profit += projected_profit
            
            projected_data.append({
                'month': month,
                'monthly_revenue': projected_revenue,
                'monthly_cost': projected_cost,
                'monthly_profit': projected_profit,
                'cumulative_revenue': cumulative_revenue,
                'cumulative_profit': cumulative_profit,
                'growth_factor': growth_factor
            })
        
        return {
            'base_monthly_revenue': monthly_revenue,
            'base_monthly_profit': monthly_profit,
            'growth_rate': growth_rate,
            'periods': periods,
            'projections': projected_data,
            'total_projected_revenue': cumulative_revenue,
            'total_projected_profit': cumulative_profit
        }
    
    def get_subscription_performance_ranking(self) -> List[Dict]:
        """Get subscription types ranked by performance"""
        results = self.calculate_comprehensive_results()
        subscriptions = results['subscriptions']
        
        # Sort by total profit
        ranked = sorted(
            subscriptions.items(),
            key=lambda x: x[1]['total_profit'],
            reverse=True
        )
        
        performance_data = []
        for rank, (name, data) in enumerate(ranked, 1):
            performance_data.append({
                'rank': rank,
                'subscription_type': name,
                'total_profit': data['total_profit'],
                'profit_margin': data['profit_margin'],
                'customers': data['customers'],
                'revenue_per_customer': data['revenue_per_customer'],
                'score': data['total_profit'] * data['profit_margin'] / 100  # Combined score
            })
        
        return performance_data
    
    def calculate_scenario_analysis(self, scenarios: Dict) -> Dict:
        """Calculate multiple scenarios for comparison"""
        scenario_results = {}
        
        for scenario_name, scenario_data in scenarios.items():
            # Temporarily update inputs
            original_inputs = self.data_manager.inputs.copy()
            
            # Apply scenario multipliers
            temp_inputs = original_inputs.copy()
            for key, value in temp_inputs.items():
                if isinstance(value, dict) and 'customers' in value:
                    temp_inputs[key]['customers'] = int(value['customers'] * scenario_data.get('customer_multiplier', 1.0))
                    temp_inputs[key]['renewals'] = int(value['renewals'] * scenario_data.get('renewal_multiplier', 1.0))
            
            self.data_manager.inputs = temp_inputs
            
            # Calculate results for this scenario
            results = self.calculate_comprehensive_results()
            scenario_results[scenario_name] = {
                'totals': results['totals'],
                'scenario_params': scenario_data
            }
            
            # Restore original inputs
            self.data_manager.inputs = original_inputs
        
        return scenario_results