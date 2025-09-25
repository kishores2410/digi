"""
24DIGI Forecasting Engine
Advanced forecasting capabilities for 3, 6, 9, 12 month projections
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from config.app_config import AppConfig
from modules.calculator import RevenueCalculator

class Forecaster:
    """Advanced forecasting engine for revenue projections"""
    
    def __init__(self, calculator: RevenueCalculator):
        """Initialize forecaster with calculator"""
        self.calculator = calculator
        self.scenarios = AppConfig.GROWTH_SCENARIOS
    
    def generate_forecast(self, periods: List[int] = None, scenarios: List[str] = None) -> Dict:
        """Generate comprehensive forecast for multiple periods and scenarios"""
        if periods is None:
            periods = AppConfig.FORECAST_PERIODS
        
        if scenarios is None:
            scenarios = list(self.scenarios.keys())
        
        forecast_data = {}
        base_results = self.calculator.calculate_comprehensive_results()
        
        for scenario_name in scenarios:
            if scenario_name not in self.scenarios:
                continue
            scenario_params = self.scenarios[scenario_name]
            forecast_data[scenario_name] = {}
            
            for period in periods:
                forecast_data[scenario_name][f"{period}_months"] = self._calculate_period_forecast(
                    base_results, scenario_params, period
                )
        
        return {
            'base_results': base_results,
            'forecasts': forecast_data,
            'scenarios_used': scenarios,
            'periods_used': periods
        }
    
    def _calculate_period_forecast(self, base_results: Dict, scenario_params: Dict, months: int) -> Dict:
        """Calculate forecast for a specific period and scenario"""
        growth_rate = scenario_params['growth_rate']
        retention_rate = scenario_params['retention_rate']

        # Check if scenario has custom pricing and/or quantity adjustments
        if 'pricing_adjustments' in scenario_params or 'quantity_adjustments' in scenario_params:
            # Apply custom pricing and quantity adjustments and recalculate base results
            quantity_adjustments = scenario_params.get('quantity_adjustments', None)
            pricing_adjustments = scenario_params.get('pricing_adjustments', {})
            adjusted_results = self._apply_pricing_adjustments(base_results, pricing_adjustments, quantity_adjustments)
            base_monthly_revenue = adjusted_results['totals']['total_revenue'] / 3
            base_monthly_cost = adjusted_results['totals']['total_cost'] / 3
        else:
            base_monthly_revenue = base_results['totals']['total_revenue'] / 3  # Convert quarterly to monthly
            base_monthly_cost = base_results['totals']['total_cost'] / 3

        base_customers = base_results['totals']['total_customers']
        
        monthly_data = []
        cumulative_revenue = 0
        cumulative_cost = 0
        cumulative_profit = 0
        
        current_customers = base_customers
        
        for month in range(1, months + 1):
            # Apply growth and retention
            new_customers = current_customers * growth_rate / 12  # Monthly growth
            retained_customers = current_customers * retention_rate
            current_customers = retained_customers + new_customers
            
            # Calculate revenue based on customer growth
            customer_growth_factor = current_customers / base_customers
            monthly_revenue = base_monthly_revenue * customer_growth_factor
            monthly_cost = base_monthly_cost * customer_growth_factor
            monthly_profit = monthly_revenue - monthly_cost
            
            cumulative_revenue += monthly_revenue
            cumulative_cost += monthly_cost
            cumulative_profit += monthly_profit
            
            # Add seasonality factor (optional)
            seasonality_factor = self._get_seasonality_factor(month)
            monthly_revenue *= seasonality_factor
            monthly_cost *= seasonality_factor
            monthly_profit = monthly_revenue - monthly_cost
            
            monthly_data.append({
                'month': month,
                'customers': int(current_customers),
                'new_customers': int(new_customers),
                'monthly_revenue': monthly_revenue,
                'monthly_cost': monthly_cost,
                'monthly_profit': monthly_profit,
                'cumulative_revenue': cumulative_revenue,
                'cumulative_cost': cumulative_cost,
                'cumulative_profit': cumulative_profit,
                'profit_margin': (monthly_profit / monthly_revenue * 100) if monthly_revenue > 0 else 0
            })
        
        return {
            'period_months': months,
            'scenario_params': scenario_params,
            'monthly_breakdown': monthly_data,
            'period_totals': {
                'total_revenue': cumulative_revenue,
                'total_cost': cumulative_cost,
                'total_profit': cumulative_profit,
                'final_customers': int(current_customers),
                'customer_growth': ((current_customers - base_customers) / base_customers * 100) if base_customers > 0 else 0,
                'profit_margin': (cumulative_profit / cumulative_revenue * 100) if cumulative_revenue > 0 else 0
            }
        }
    
    def _get_seasonality_factor(self, month: int) -> float:
        """Get seasonality factor for a given month (1-12)"""
        # Simple seasonality model - you can make this more sophisticated
        seasonality_map = {
            1: 0.9,   # January - slower
            2: 0.95,  # February
            3: 1.1,   # March - Q1 push
            4: 1.0,   # April
            5: 1.0,   # May
            6: 1.05,  # June - Q2 end
            7: 0.95,  # July - summer slowdown
            8: 0.9,   # August
            9: 1.1,   # September - back to business
            10: 1.05, # October
            11: 1.15, # November - holiday prep
            12: 1.2   # December - year end push
        }
        
        month_index = ((month - 1) % 12) + 1
        return seasonality_map.get(month_index, 1.0)
    
    def compare_scenarios(self, period_months: int = 12) -> Dict:
        """Compare all scenarios for a specific period"""
        comparison_data = {}
        base_results = self.calculator.calculate_comprehensive_results()
        
        for scenario_name, scenario_params in self.scenarios.items():
            forecast = self._calculate_period_forecast(base_results, scenario_params, period_months)
            comparison_data[scenario_name] = {
                'total_revenue': forecast['period_totals']['total_revenue'],
                'total_profit': forecast['period_totals']['total_profit'],
                'profit_margin': forecast['period_totals']['profit_margin'],
                'final_customers': forecast['period_totals']['final_customers'],
                'customer_growth': forecast['period_totals']['customer_growth'],
                'growth_rate': scenario_params['growth_rate'],
                'retention_rate': scenario_params['retention_rate']
            }
        
        return comparison_data
    
    def calculate_break_even_analysis(self, fixed_costs: float = 0) -> Dict:
        """Calculate break-even analysis for different scenarios"""
        base_results = self.calculator.calculate_comprehensive_results()
        
        # Calculate average profit per customer
        avg_profit_per_customer = base_results['totals']['profit_per_customer']
        
        break_even_data = {}
        
        for scenario_name, scenario_params in self.scenarios.items():
            # Calculate break-even customers needed
            break_even_customers = fixed_costs / avg_profit_per_customer if avg_profit_per_customer > 0 else float('inf')
            
            # Calculate time to break even based on growth rate
            current_customers = base_results['totals']['total_customers']
            monthly_growth_rate = scenario_params['growth_rate'] / 12
            
            if monthly_growth_rate > 0 and break_even_customers > current_customers:
                months_to_break_even = np.log(break_even_customers / current_customers) / np.log(1 + monthly_growth_rate)
            else:
                months_to_break_even = 0 if current_customers >= break_even_customers else float('inf')
            
            break_even_data[scenario_name] = {
                'break_even_customers': int(break_even_customers) if break_even_customers != float('inf') else 'N/A',
                'current_customers': current_customers,
                'months_to_break_even': months_to_break_even if months_to_break_even != float('inf') else 'Never',
                'monthly_growth_rate': monthly_growth_rate * 100,
                'avg_profit_per_customer': avg_profit_per_customer
            }
        
        return break_even_data
    
    def generate_sensitivity_analysis(self, base_period: int = 12) -> Dict:
        """Generate sensitivity analysis for key parameters"""
        base_results = self.calculator.calculate_comprehensive_results()
        
        # Parameters to test
        growth_rates = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
        retention_rates = [0.80, 0.85, 0.90, 0.95, 0.98]
        
        sensitivity_data = {
            'growth_rate_sensitivity': [],
            'retention_rate_sensitivity': []
        }
        
        # Test growth rate sensitivity (with base retention)
        base_retention = 0.90
        for growth_rate in growth_rates:
            scenario_params = {'growth_rate': growth_rate, 'retention_rate': base_retention}
            forecast = self._calculate_period_forecast(base_results, scenario_params, base_period)
            
            sensitivity_data['growth_rate_sensitivity'].append({
                'growth_rate': growth_rate * 100,
                'total_revenue': forecast['period_totals']['total_revenue'],
                'total_profit': forecast['period_totals']['total_profit'],
                'final_customers': forecast['period_totals']['final_customers']
            })
        
        # Test retention rate sensitivity (with base growth)
        base_growth = 0.15
        for retention_rate in retention_rates:
            scenario_params = {'growth_rate': base_growth, 'retention_rate': retention_rate}
            forecast = self._calculate_period_forecast(base_results, scenario_params, base_period)
            
            sensitivity_data['retention_rate_sensitivity'].append({
                'retention_rate': retention_rate * 100,
                'total_revenue': forecast['period_totals']['total_revenue'],
                'total_profit': forecast['period_totals']['total_profit'],
                'final_customers': forecast['period_totals']['final_customers']
            })
        
        return sensitivity_data
    
    def create_forecast_dataframe(self, forecast_data: Dict) -> pd.DataFrame:
        """Create a DataFrame from forecast data for easy analysis"""
        rows = []
        
        for scenario_name, scenario_forecasts in forecast_data['forecasts'].items():
            for period_name, period_data in scenario_forecasts.items():
                period_months = period_data['period_months']
                totals = period_data['period_totals']
                
                rows.append({
                    'Scenario': scenario_name,
                    'Period (Months)': period_months,
                    'Total Revenue': totals['total_revenue'],
                    'Total Cost': totals['total_cost'],
                    'Total Profit': totals['total_profit'],
                    'Profit Margin (%)': totals['profit_margin'],
                    'Final Customers': totals['final_customers'],
                    'Customer Growth (%)': totals['customer_growth'],
                    'Growth Rate': period_data['scenario_params']['growth_rate'],
                    'Retention Rate': period_data['scenario_params']['retention_rate']
                })
        
        return pd.DataFrame(rows)

    def _apply_pricing_adjustments(self, base_results: Dict, pricing_adjustments: Dict, quantity_adjustments: Dict = None) -> Dict:
        """Apply custom pricing and quantity adjustments to base results"""
        # Create a copy of base results to modify
        adjusted_results = base_results.copy()

        # Temporarily modify the calculator's pricing and input data
        original_pricing = self.calculator.data_manager.pricing_data.copy()
        original_inputs = self.calculator.data_manager.inputs.copy()

        # Apply quantity adjustments first if provided
        if quantity_adjustments:
            # Temporarily set the modified inputs
            self.calculator.data_manager.inputs = quantity_adjustments
            # Update session state as well
            import streamlit as st
            st.session_state.input_data = quantity_adjustments

        # Find which subscription type this pricing belongs to
        for sub_type in ['VIP', 'Normal', 'Custom']:
            if sub_type in original_pricing:
                # Apply the pricing adjustments
                modified_pricing = original_pricing.copy()
                modified_pricing[sub_type] = pricing_adjustments

                # Temporarily set the modified pricing
                self.calculator.data_manager.pricing_data = modified_pricing

                # Recalculate with new pricing and quantities
                adjusted_results = self.calculator.calculate_comprehensive_results()
                break

        # Restore original pricing and inputs
        self.calculator.data_manager.pricing_data = original_pricing
        self.calculator.data_manager.inputs = original_inputs

        return adjusted_results
