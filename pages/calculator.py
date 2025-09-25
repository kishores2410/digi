"""
24DIGI Calculator Page
Comprehensive input interface for all subscription combinations
"""

import streamlit as st
import pandas as pd
from modules.data_manager import DataManager
from modules.calculator import RevenueCalculator
from config.app_config import AppConfig

def render(data_manager: DataManager, calculator: RevenueCalculator):
    """Render the calculator page"""
    
    st.header("🧮 Revenue Calculator")
    st.markdown("*Configure all subscription types and durations simultaneously*")
    
    # Create expandable sections for better organization
    with st.expander("📋 Subscription Configurations", expanded=True):
        render_subscription_inputs(data_manager)
    
    with st.expander("🛠️ Additional Services", expanded=True):
        render_additional_services_inputs(data_manager)
    
    with st.expander("🎯 Events & Activities", expanded=True):
        render_events_inputs(data_manager)
    
    # Calculate and display results
    st.markdown("---")
    st.header("💰 Calculation Results")
    
    results = calculator.calculate_comprehensive_results()
    display_calculation_results(results)

def render_subscription_inputs(data_manager: DataManager):
    """Render subscription input controls"""
    st.subheader("🔄 Subscription Matrix")
    st.markdown("*Configure customers and renewals for all subscription combinations*")
    
    # Create a grid for subscription inputs
    combinations = data_manager.get_subscription_combinations()
    
    # Group by subscription type for better layout
    subscription_types = {}
    for combo in combinations:
        if combo['type'] not in subscription_types:
            subscription_types[combo['type']] = []
        subscription_types[combo['type']].append(combo)
    
    for sub_type, combos in subscription_types.items():
        st.markdown(f"#### {sub_type} Subscriptions")
        
        cols = st.columns(len(combos))
        
        for i, combo in enumerate(combos):
            with cols[i]:
                key = combo['key']
                
                st.markdown(f"**{combo['duration']} Month{'s' if combo['duration'] > 1 else ''}**")
                
                # Get current values
                current_data = data_manager.inputs.get(key, {'customers': 0, 'renewals': 0})
                
                # Customer input
                customers = st.number_input(
                    "Customers",
                    min_value=0,
                    value=current_data.get('customers', 0),
                    step=1,
                    key=f"customers_{key}"
                )
                
                # Renewals input
                renewals = st.number_input(
                    "Renewals",
                    min_value=0,
                    value=current_data.get('renewals', 0),
                    step=1,
                    key=f"renewals_{key}"
                )
                
                # Update data manager
                data_manager.update_input_data({
                    key: {'customers': customers, 'renewals': renewals}
                })
                
                # Show package cost
                package_data = data_manager.calculate_package_cost(combo['type'], combo['duration'])
                st.info(f"📦 Package: {package_data['cost']:,.0f} → {package_data['revenue']:,.0f} AED")
                
                if customers > 0:
                    total_revenue = package_data['revenue'] * customers + (renewals * (1500 if combo['duration'] == 1 else 4500))
                    st.success(f"💰 Total: {total_revenue:,.0f} AED")

def render_additional_services_inputs(data_manager: DataManager):
    """Render additional services input controls"""
    st.subheader("🛠️ Additional Services Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔗 Bracelet Services**")
        
        additional_bracelets = st.number_input(
            "Additional Bracelets",
            min_value=0,
            value=data_manager.inputs.get('additional_bracelets', 100),
            step=1,
            help="Bracelets sold beyond subscription packages"
        )
        
        bracelets_non_subscribers = st.number_input(
            "Bracelets for Non-Subscribers",
            min_value=0,
            value=data_manager.inputs.get('bracelets_non_subscribers', 75),
            step=1
        )
        
        data_manager.update_input_data({
            'additional_bracelets': additional_bracelets,
            'bracelets_non_subscribers': bracelets_non_subscribers
        })
    
    with col2:
        st.markdown("**🤖 CBYI Services**")
        
        cbyi_non_subscribers = st.number_input(
            "CBYI Non-Subscribers",
            min_value=0,
            value=data_manager.inputs.get('cbyi_non_subscribers', 50),
            step=1,
            help="C By AI services for non-subscribers"
        )
        
        data_manager.update_input_data({
            'cbyi_non_subscribers': cbyi_non_subscribers
        })
        
        # Show CBYI pricing
        cbyi_pricing = data_manager.get_pricing_data('Custom').get('cbyiOneMonth', {})
        if cbyi_pricing:
            st.info(f"CBYI Rate: {cbyi_pricing.get('selling', 0):,.0f} AED")
    
    with col3:
        st.markdown("**🚗 Car Rental**")
        
        car_rental_customers = st.number_input(
            "Car Rental Customers",
            min_value=0,
            value=data_manager.inputs.get('car_rental_customers', 20),
            step=1
        )
        
        car_rental_period = st.selectbox(
            "Car Rental Period",
            [1, 3],
            index=0,
            format_func=lambda x: f"{x} Month{'s' if x > 1 else ''}"
        )
        
        data_manager.update_input_data({
            'car_rental_customers': car_rental_customers,
            'car_rental_period': car_rental_period
        })

def render_events_inputs(data_manager: DataManager):
    """Render events and activities input controls"""
    st.subheader("🎯 Events & Activities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🏆 Challenges**")
        
        challenge_fee = st.number_input(
            "Challenge Fee (AED)",
            min_value=0.0,
            value=float(data_manager.inputs.get('challenge_fee', 25.0)),
            step=0.1
        )
        
        challenge_participants = st.number_input(
            "Challenge Participants",
            min_value=0,
            value=data_manager.inputs.get('challenge_participants', 200),
            step=1
        )
        
        challenge_revenue = challenge_fee * challenge_participants
        st.success(f"💰 Challenge Revenue: {challenge_revenue:,.0f} AED")
        
        data_manager.update_input_data({
            'challenge_fee': challenge_fee,
            'challenge_participants': challenge_participants
        })
    
    with col2:
        st.markdown("**🗺️ Adventures**")
        
        adventure_fee = st.number_input(
            "Adventure Fee (AED)",
            min_value=0.0,
            value=float(data_manager.inputs.get('adventure_fee', 40.0)),
            step=0.1
        )
        
        adventure_participants = st.number_input(
            "Adventure Participants",
            min_value=0,
            value=data_manager.inputs.get('adventure_participants', 150),
            step=1
        )
        
        adventure_revenue = adventure_fee * adventure_participants
        st.success(f"💰 Adventure Revenue: {adventure_revenue:,.0f} AED")
        
        data_manager.update_input_data({
            'adventure_fee': adventure_fee,
            'adventure_participants': adventure_participants
        })
    
    with col3:
        st.markdown("**🥇 Competitions**")
        
        competition_fee = st.number_input(
            "Competition Fee (AED)",
            min_value=0.0,
            value=float(data_manager.inputs.get('competition_fee', 35.0)),
            step=0.1
        )
        
        competition_participants = st.number_input(
            "Competition Participants",
            min_value=0,
            value=data_manager.inputs.get('competition_participants', 100),
            step=1
        )
        
        competition_revenue = competition_fee * competition_participants
        st.success(f"💰 Competition Revenue: {competition_revenue:,.0f} AED")
        
        data_manager.update_input_data({
            'competition_fee': competition_fee,
            'competition_participants': competition_participants
        })

def display_calculation_results(results):
    """Display comprehensive calculation results"""
    totals = results['totals']
    
    # Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"{totals['total_revenue']:,.0f} AED")
    
    with col2:
        st.metric("Total Cost", f"{totals['total_cost']:,.0f} AED")
    
    with col3:
        st.metric("Total Profit", f"{totals['total_profit']:,.0f} AED")
    
    with col4:
        st.metric("Profit Margin", f"{totals['profit_margin']:.1f}%")
    
    # Detailed Breakdown
    st.subheader("📊 Detailed Breakdown")
    
    # Subscription Results
    if results['subscriptions']:
        st.markdown("#### 🔄 Subscription Performance")
        
        subscription_data = []
        for name, data in results['subscriptions'].items():
            subscription_data.append({
                'Subscription': name,
                'Customers': f"{data['customers']:,}",
                'Renewals': f"{data['renewals']:,}",
                'Cost per Customer': f"{data['cost_per_customer']:,.0f} AED",
                'Revenue per Customer': f"{data['revenue_per_customer']:,.0f} AED",
                'Total Revenue': f"{data['total_revenue']:,.0f} AED",
                'Total Profit': f"{data['total_profit']:,.0f} AED",
                'Margin': f"{data['profit_margin']:.1f}%"
            })
        
        df_subscriptions = pd.DataFrame(subscription_data)
        st.dataframe(df_subscriptions, use_container_width=True, hide_index=True)
    
    # Additional Services
    if results['additional_services']:
        st.markdown("#### 🛠️ Additional Services Performance")
        
        services_data = []
        for name, data in results['additional_services'].items():
            if data['revenue'] > 0:
                services_data.append({
                    'Service': name,
                    'Cost': f"{data['cost']:,.0f} AED",
                    'Revenue': f"{data['revenue']:,.0f} AED",
                    'Profit': f"{data['profit']:,.0f} AED",
                    'Margin': f"{(data['profit']/data['revenue']*100) if data['revenue'] > 0 else 0:.1f}%"
                })
        
        if services_data:
            df_services = pd.DataFrame(services_data)
            st.dataframe(df_services, use_container_width=True, hide_index=True)
    
    # VIP Verification
    vip_3_month = None
    for name, data in results['subscriptions'].items():
        if 'VIP - 3' in name:
            vip_3_month = data
            break
    
    if vip_3_month and vip_3_month['customers'] > 0:
        expected_cost_per_customer = 4215
        expected_revenue_per_customer = 6650
        
        cost_match = abs(vip_3_month['cost_per_customer'] - expected_cost_per_customer) < 1
        revenue_match = abs(vip_3_month['revenue_per_customer'] - expected_revenue_per_customer) < 1
        
        if cost_match and revenue_match:
            st.success(f"✅ VIP 3-month verification passed: {vip_3_month['cost_per_customer']:,.0f} AED cost, {vip_3_month['revenue_per_customer']:,.0f} AED revenue per customer")
        else:
            st.warning(f"⚠️ VIP 3-month verification: Expected 4,215/6,650 AED, got {vip_3_month['cost_per_customer']:,.0f}/{vip_3_month['revenue_per_customer']:,.0f} AED")
    
    # Action Buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reset All Inputs", type="secondary"):
            # Reset to defaults
            for key, default_value in AppConfig.DEFAULT_INPUTS.items():
                if isinstance(default_value, dict):
                    st.session_state.input_data[key] = default_value.copy()
            st.rerun()
    
    with col2:
        if st.button("📈 View Analytics", type="primary"):
            st.info("Switch to Analytics tab for detailed visualizations")
    
    with col3:
        if st.button("🔮 Generate Forecast", type="primary"):
            st.info("Switch to Forecasting tab for future projections")
