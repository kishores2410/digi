"""
24DIGI Forecasting Page
Advanced forecasting for 3, 6, 9, 12 month projections
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from modules.forecaster import Forecaster
from config.app_config import AppConfig

def render(forecaster: Forecaster):
    """Render the forecasting page"""
    
    st.header("🔮 Revenue Forecasting")
    st.markdown("*Advanced predictive analytics for strategic planning*")
    
    # Forecasting Controls
    with st.expander("⚙️ Forecasting Parameters", expanded=True):
        render_forecast_controls(forecaster)
    
    # Generate forecasts based on current settings
    forecast_periods = st.session_state.get('forecast_periods', [3, 6, 9, 12])
    forecast_scenarios = st.session_state.get('forecast_scenarios', list(AppConfig.GROWTH_SCENARIOS.keys()))

    # Build complete scenarios list including parameter scenarios
    all_scenarios = set(AppConfig.GROWTH_SCENARIOS.keys())
    if 'parameter_scenarios' in st.session_state:
        param_scenario_names = {scenario['name'] for scenario in st.session_state.parameter_scenarios.values()}
        all_scenarios.update(param_scenario_names)

    # Filter out invalid scenarios
    forecast_scenarios = [s for s in forecast_scenarios if s in all_scenarios]
    
    # Update forecaster with parameter scenarios before generating forecasts
    if 'parameter_scenarios' in st.session_state:
        for scenario_key, scenario_data in st.session_state.parameter_scenarios.items():
            forecaster.scenarios[scenario_data['name']] = {
                'growth_rate': scenario_data['growth_rate'],
                'retention_rate': scenario_data['retention_rate'],
                'pricing_adjustments': scenario_data['pricing']
            }

    with st.spinner("🔄 Generating forecasts..."):
        forecast_data = forecaster.generate_forecast(forecast_periods, forecast_scenarios)
    
    # Display forecast results
    render_forecast_results(forecast_data, forecaster)

def render_forecast_controls(forecaster: Forecaster):
    """Render forecasting control inputs"""
    st.subheader("📊 Forecast Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📅 Forecast Periods**")
        
        # Multi-select for periods
        selected_periods = st.multiselect(
            "Select forecast periods (months)",
            options=[3, 6, 9, 12, 18, 24],
            default=[3, 6, 9, 12],
            help="Choose the time horizons for forecasting"
        )
        
        if not selected_periods:
            selected_periods = [12]  # Default fallback
        
        st.session_state.forecast_periods = selected_periods
    
    with col2:
        st.markdown("**📈 Growth Scenarios**")
        
        # Multi-select for scenarios
        available_scenarios = list(AppConfig.GROWTH_SCENARIOS.keys())

        # Add parameter scenarios if they exist
        if 'parameter_scenarios' in st.session_state:
            param_scenario_names = [scenario['name'] for scenario in st.session_state.parameter_scenarios.values()]
            available_scenarios.extend(param_scenario_names)

        selected_scenarios = st.multiselect(
            "Select growth scenarios",
            options=available_scenarios,
            default=[s for s in available_scenarios if s in AppConfig.GROWTH_SCENARIOS],
            help="Choose scenarios to compare"
        )
        
        if not selected_scenarios:
            selected_scenarios = ["Moderate"]  # Default fallback
        
        st.session_state.forecast_scenarios = selected_scenarios
    
    # Scenario Details
    st.markdown("**🎯 Scenario Parameters**")
    scenario_details = []
    for scenario in selected_scenarios:
        if scenario in AppConfig.GROWTH_SCENARIOS:
            params = AppConfig.GROWTH_SCENARIOS[scenario]
            scenario_type = "Standard"
        elif 'parameter_scenarios' in st.session_state:
            # Check if it's a parameter scenario
            param_scenario = None
            for scenario_data in st.session_state.parameter_scenarios.values():
                if scenario_data['name'] == scenario:
                    param_scenario = scenario_data
                    break
            if param_scenario:
                params = {
                    'growth_rate': param_scenario['growth_rate'],
                    'retention_rate': param_scenario['retention_rate']
                }
                scenario_type = f"Parameter ({param_scenario['base_type']})"
            else:
                continue
        else:
            continue

        scenario_details.append({
            'Scenario': scenario,
            'Type': scenario_type,
            'Growth Rate': f"{params['growth_rate']*100:.1f}%",
            'Retention Rate': f"{params['retention_rate']*100:.1f}%"
        })
    
    df_scenarios = pd.DataFrame(scenario_details)
    st.dataframe(df_scenarios, use_container_width=True, hide_index=True)
    
    # Custom Scenario Builder
    with st.expander("🛠️ Custom Scenario Builder"):
        render_custom_scenario_builder()

    # Parameter-Based Scenario Builder
    with st.expander("⚙️ Parameter-Based Scenario Builder"):
        render_parameter_scenario_builder(forecaster)

    # Scenario Management
    with st.expander("🗂️ Scenario Management"):
        render_scenario_management()

def render_custom_scenario_builder():
    """Render custom scenario creation interface"""
    st.markdown("**Create Custom Scenario**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        custom_name = st.text_input("Scenario Name", value="Custom", key="custom_scenario_name")
    
    with col2:
        custom_growth = st.slider("Annual Growth Rate (%)", 0, 100, 20, key="custom_scenario_growth") / 100

    with col3:
        custom_retention = st.slider("Retention Rate (%)", 70, 99, 90, key="custom_scenario_retention") / 100
    
    if st.button("➕ Add Custom Scenario", key="add_custom_scenario"):
        if custom_name and custom_name not in AppConfig.GROWTH_SCENARIOS:
            AppConfig.GROWTH_SCENARIOS[custom_name] = {
                'growth_rate': custom_growth,
                'retention_rate': custom_retention
            }
            st.success(f"✅ Added custom scenario: {custom_name}")
            st.rerun()
        else:
            st.error("Please provide a unique scenario name")

def render_parameter_scenario_builder(forecaster):
    """Render parameter-based scenario creation interface"""
    st.markdown("**Create Parameter-Based Scenario**")
    st.markdown("*Adjust service prices and parameters (excluding car rental)*")

    # Get current pricing data
    data_manager = forecaster.calculator.data_manager
    current_pricing = data_manager.get_pricing_data()

    col1, col2 = st.columns(2)

    with col1:
        scenario_name = st.text_input("Parameter Scenario Name", value="Price Adjusted", key="param_scenario_name")

    with col2:
        subscription_type = st.selectbox("Base Subscription Type", ['VIP', 'Normal', 'Custom'], key="param_subscription_type")

    st.markdown("**Adjust Service Parameters:**")

    # Create tabs for different parameter categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 Subscribers", "🍽️ Meals & Services", "📿 Bracelets", "🎮 Events & Games", "💰 Pricing"])

    # Get current input data for quantities
    current_inputs = data_manager.get_input_data()
    adjusted_inputs = current_inputs.copy()
    adjusted_pricing = current_pricing[subscription_type].copy()

    with tab1:
        st.markdown("**Subscription Numbers**")

        # VIP Subscribers
        st.markdown("**VIP Subscribers:**")
        col1, col2 = st.columns(2)
        with col1:
            adjusted_inputs['VIP_1_month']['customers'] = st.number_input(
                "VIP 1-Month Customers",
                value=int(adjusted_inputs['VIP_1_month']['customers']),
                min_value=0,
                step=5,
                key="param_vip_1m_customers"
            )
            adjusted_inputs['VIP_1_month']['renewals'] = st.number_input(
                "VIP 1-Month Renewals",
                value=int(adjusted_inputs['VIP_1_month']['renewals']),
                min_value=0,
                step=5,
                key="param_vip_1m_renewals"
            )
        with col2:
            adjusted_inputs['VIP_3_months']['customers'] = st.number_input(
                "VIP 3-Month Customers",
                value=int(adjusted_inputs['VIP_3_months']['customers']),
                min_value=0,
                step=10,
                key="param_vip_3m_customers"
            )
            adjusted_inputs['VIP_3_months']['renewals'] = st.number_input(
                "VIP 3-Month Renewals",
                value=int(adjusted_inputs['VIP_3_months']['renewals']),
                min_value=0,
                step=10,
                key="param_vip_3m_renewals"
            )

        # Normal Subscribers
        st.markdown("**Normal Subscribers:**")
        col1, col2 = st.columns(2)
        with col1:
            adjusted_inputs['Normal_1_month']['customers'] = st.number_input(
                "Normal 1-Month Customers",
                value=int(adjusted_inputs['Normal_1_month']['customers']),
                min_value=0,
                step=10,
                key="param_normal_1m_customers"
            )
            adjusted_inputs['Normal_1_month']['renewals'] = st.number_input(
                "Normal 1-Month Renewals",
                value=int(adjusted_inputs['Normal_1_month']['renewals']),
                min_value=0,
                step=10,
                key="param_normal_1m_renewals"
            )
        with col2:
            adjusted_inputs['Normal_3_months']['customers'] = st.number_input(
                "Normal 3-Month Customers",
                value=int(adjusted_inputs['Normal_3_months']['customers']),
                min_value=0,
                step=10,
                key="param_normal_3m_customers"
            )
            adjusted_inputs['Normal_3_months']['renewals'] = st.number_input(
                "Normal 3-Month Renewals",
                value=int(adjusted_inputs['Normal_3_months']['renewals']),
                min_value=0,
                step=10,
                key="param_normal_3m_renewals"
            )

        # Custom Subscribers
        st.markdown("**Custom Subscribers:**")
        col1, col2 = st.columns(2)
        with col1:
            adjusted_inputs['Custom_1_month']['customers'] = st.number_input(
                "Custom 1-Month Customers",
                value=int(adjusted_inputs['Custom_1_month']['customers']),
                min_value=0,
                step=5,
                key="param_custom_1m_customers"
            )
            adjusted_inputs['Custom_1_month']['renewals'] = st.number_input(
                "Custom 1-Month Renewals",
                value=int(adjusted_inputs['Custom_1_month']['renewals']),
                min_value=0,
                step=5,
                key="param_custom_1m_renewals"
            )
        with col2:
            adjusted_inputs['Custom_3_months']['customers'] = st.number_input(
                "Custom 3-Month Customers",
                value=int(adjusted_inputs['Custom_3_months']['customers']),
                min_value=0,
                step=5,
                key="param_custom_3m_customers"
            )
            adjusted_inputs['Custom_3_months']['renewals'] = st.number_input(
                "Custom 3-Month Renewals",
                value=int(adjusted_inputs['Custom_3_months']['renewals']),
                min_value=0,
                step=5,
                key="param_custom_3m_renewals"
            )

    with tab2:
        st.markdown("**Additional Services & CBYI**")
        col1, col2 = st.columns(2)

        with col1:
            adjusted_inputs['cbyi_non_subscribers'] = st.number_input(
                "CBYI Non-Subscribers",
                value=int(adjusted_inputs['cbyi_non_subscribers']),
                min_value=0,
                step=5,
                key="param_cbyi_non_subs"
            )

        with col2:
            adjusted_inputs['car_rental_customers'] = st.number_input(
                "Car Rental Customers",
                value=int(adjusted_inputs['car_rental_customers']),
                min_value=0,
                step=5,
                key="param_car_rental"
            )

    with tab3:
        st.markdown("**Bracelet Quantities**")
        col1, col2 = st.columns(2)

        with col1:
            adjusted_inputs['additional_bracelets'] = st.number_input(
                "Additional Bracelets",
                value=int(adjusted_inputs['additional_bracelets']),
                min_value=0,
                step=10,
                key="param_additional_bracelets"
            )

        with col2:
            adjusted_inputs['bracelets_non_subscribers'] = st.number_input(
                "Bracelets for Non-Subscribers",
                value=int(adjusted_inputs['bracelets_non_subscribers']),
                min_value=0,
                step=5,
                key="param_bracelets_non_subs"
            )

    with tab4:
        st.markdown("**Events & Games Participation**")
        col1, col2 = st.columns(2)

        with col1:
            adjusted_inputs['challenge_participants'] = st.number_input(
                "Challenge Participants",
                value=int(adjusted_inputs['challenge_participants']),
                min_value=0,
                step=10,
                key="param_challenge_participants"
            )
            adjusted_inputs['adventure_participants'] = st.number_input(
                "Adventure Participants",
                value=int(adjusted_inputs['adventure_participants']),
                min_value=0,
                step=10,
                key="param_adventure_participants"
            )

        with col2:
            adjusted_inputs['competition_participants'] = st.number_input(
                "Competition Participants",
                value=int(adjusted_inputs['competition_participants']),
                min_value=0,
                step=5,
                key="param_competition_participants"
            )

        st.markdown("**Event Fees:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            adjusted_inputs['challenge_fee'] = st.number_input(
                "Challenge Fee (AED)",
                value=float(adjusted_inputs['challenge_fee']),
                min_value=0.0,
                step=5.0,
                key="param_challenge_fee"
            )
        with col2:
            adjusted_inputs['adventure_fee'] = st.number_input(
                "Adventure Fee (AED)",
                value=float(adjusted_inputs['adventure_fee']),
                min_value=0.0,
                step=5.0,
                key="param_adventure_fee"
            )
        with col3:
            adjusted_inputs['competition_fee'] = st.number_input(
                "Competition Fee (AED)",
                value=float(adjusted_inputs['competition_fee']),
                min_value=0.0,
                step=5.0,
                key="param_competition_fee"
            )

    with tab5:
        st.markdown("**Service Pricing (Optional)**")
        st.markdown("*Adjust prices if needed - quantities are the main focus*")

        col1, col2 = st.columns(2)
        with col1:
            if 'mealsPerMonth' in adjusted_pricing:
                adjusted_pricing['mealsPerMonth']['selling'] = st.number_input(
                    "Monthly Meals Price",
                    value=float(adjusted_pricing['mealsPerMonth']['selling']),
                    min_value=0.0,
                    step=50.0,
                    key="param_meals_monthly_price"
                )

            if 'digitalProfit' in adjusted_pricing:
                adjusted_pricing['digitalProfit'] = st.number_input(
                    "Digital Profit",
                    value=float(adjusted_pricing['digitalProfit']),
                    min_value=0.0,
                    step=50.0,
                    key="param_digital_profit_price"
                )

        with col2:
            if 'bracelet' in adjusted_pricing:
                adjusted_pricing['bracelet']['selling'] = st.number_input(
                    "Bracelet Price",
                    value=float(adjusted_pricing['bracelet']['selling']),
                    min_value=0.0,
                    step=25.0,
                    key="param_bracelet_price"
                )

    # Recalculate profits based on adjusted selling prices
    for service, data in adjusted_pricing.items():
        if isinstance(data, dict) and 'cost' in data and 'selling' in data:
            data['profit'] = data['selling'] - data['cost']

    st.markdown("---")

    # Use default moderate growth parameters for parameter scenarios
    growth_rate = 0.15  # 15% default
    retention_rate = 0.90  # 90% default

    if st.button("🚀 Create Parameter Scenario", key="create_parameter_scenario"):
        if scenario_name:
            # Create a new scenario with adjusted parameters
            scenario_key = f"param_{scenario_name}_{subscription_type}"

            # Store the scenario in session state for use in forecasting
            if 'parameter_scenarios' not in st.session_state:
                st.session_state.parameter_scenarios = {}

            st.session_state.parameter_scenarios[scenario_key] = {
                'name': scenario_name,
                'base_type': subscription_type,
                'pricing': adjusted_pricing,
                'quantities': adjusted_inputs,  # Store quantity adjustments
                'growth_rate': growth_rate,
                'retention_rate': retention_rate
            }

            # Also add to growth scenarios for compatibility
            AppConfig.GROWTH_SCENARIOS[scenario_name] = {
                'growth_rate': growth_rate,
                'retention_rate': retention_rate,
                'pricing_adjustments': adjusted_pricing,
                'quantity_adjustments': adjusted_inputs  # Store quantity adjustments
            }

            st.success(f"✅ Created parameter scenario: {scenario_name}")
            st.success(f"📊 Includes {len([k for k in adjusted_inputs.keys() if 'customers' in k or 'participants' in k or 'bracelets' in k or 'cbyi' in k])} quantity parameters")
            st.rerun()
        else:
            st.error("Please provide a scenario name")

def render_scenario_management():
    """Render scenario management interface for deleting custom scenarios"""
    st.markdown("**Manage Custom Scenarios**")
    st.markdown("*View and delete your custom created scenarios*")

    # Get all custom scenarios
    custom_scenarios_from_config = []
    parameter_scenarios_from_session = []

    # Get scenarios from AppConfig (custom growth scenarios)
    default_scenarios = {'Conservative', 'Moderate', 'Aggressive', 'Optimistic'}
    for scenario_name in AppConfig.GROWTH_SCENARIOS.keys():
        if scenario_name not in default_scenarios:
            custom_scenarios_from_config.append(scenario_name)

    # Get parameter scenarios from session state
    if 'parameter_scenarios' in st.session_state:
        for scenario_data in st.session_state.parameter_scenarios.values():
            parameter_scenarios_from_session.append(scenario_data['name'])

    total_custom_scenarios = len(custom_scenarios_from_config) + len(parameter_scenarios_from_session)

    if total_custom_scenarios == 0:
        st.info("No custom scenarios created yet. Create some scenarios using the builders above!")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🎯 Standard Custom Scenarios**")
        if custom_scenarios_from_config:
            for scenario_name in custom_scenarios_from_config:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    params = AppConfig.GROWTH_SCENARIOS[scenario_name]
                    st.write(f"**{scenario_name}** - Growth: {params['growth_rate']*100:.1f}%, Retention: {params['retention_rate']*100:.1f}%")
                with col_b:
                    if st.button("🗑️", key=f"delete_standard_{scenario_name}", help=f"Delete {scenario_name}"):
                        # Delete from AppConfig
                        del AppConfig.GROWTH_SCENARIOS[scenario_name]
                        # Clear from session state if it exists
                        if 'forecast_scenarios' in st.session_state and scenario_name in st.session_state.forecast_scenarios:
                            st.session_state.forecast_scenarios = [s for s in st.session_state.forecast_scenarios if s != scenario_name]
                        st.success(f"✅ Deleted scenario: {scenario_name}")
                        st.rerun()
        else:
            st.write("*No standard custom scenarios*")

    with col2:
        st.markdown("**⚙️ Parameter-Based Scenarios**")
        if parameter_scenarios_from_session:
            for scenario_name in parameter_scenarios_from_session:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    # Find the scenario data
                    scenario_data = None
                    for key, data in st.session_state.parameter_scenarios.items():
                        if data['name'] == scenario_name:
                            scenario_data = data
                            break

                    if scenario_data:
                        st.write(f"**{scenario_name}** ({scenario_data['base_type']}) - Growth: {scenario_data['growth_rate']*100:.1f}%, Retention: {scenario_data['retention_rate']*100:.1f}%")

                with col_b:
                    if st.button("🗑️", key=f"delete_param_{scenario_name}", help=f"Delete {scenario_name}"):
                        # Delete from session state parameter scenarios
                        keys_to_delete = [key for key, data in st.session_state.parameter_scenarios.items() if data['name'] == scenario_name]
                        for key in keys_to_delete:
                            del st.session_state.parameter_scenarios[key]

                        # Delete from AppConfig if it exists there
                        if scenario_name in AppConfig.GROWTH_SCENARIOS:
                            del AppConfig.GROWTH_SCENARIOS[scenario_name]

                        # Clear from session state forecast scenarios if it exists
                        if 'forecast_scenarios' in st.session_state and scenario_name in st.session_state.forecast_scenarios:
                            st.session_state.forecast_scenarios = [s for s in st.session_state.forecast_scenarios if s != scenario_name]

                        st.success(f"✅ Deleted parameter scenario: {scenario_name}")
                        st.rerun()
        else:
            st.write("*No parameter-based scenarios*")

    st.markdown("---")

    # Bulk delete option
    if total_custom_scenarios > 1:
        st.markdown("**🚨 Bulk Actions**")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Delete All Custom Scenarios", key="delete_all_scenarios"):
                # Delete all custom scenarios from AppConfig
                default_scenarios = {'Conservative', 'Moderate', 'Aggressive', 'Optimistic'}
                scenarios_to_delete = [name for name in AppConfig.GROWTH_SCENARIOS.keys() if name not in default_scenarios]
                for scenario_name in scenarios_to_delete:
                    del AppConfig.GROWTH_SCENARIOS[scenario_name]

                # Clear parameter scenarios from session state
                if 'parameter_scenarios' in st.session_state:
                    st.session_state.parameter_scenarios = {}

                # Clear forecast scenarios from session state
                if 'forecast_scenarios' in st.session_state:
                    st.session_state.forecast_scenarios = list(default_scenarios)

                st.success(f"✅ Deleted all {total_custom_scenarios} custom scenarios")
                st.rerun()

        with col2:
            st.write(f"📊 Total custom scenarios: **{total_custom_scenarios}**")

def render_forecast_results(forecast_data, forecaster):
    """Render comprehensive forecast results"""
    
    # Summary Cards
    st.subheader("📊 Forecast Summary")
    render_forecast_summary_cards(forecast_data)
    
    # Charts
    st.subheader("📈 Forecast Visualizations")
    render_forecast_charts(forecast_data)
    
    # Detailed Tables
    st.subheader("📋 Detailed Projections")
    render_forecast_tables(forecast_data, forecaster)
    
    # Scenario Comparison
    st.subheader("⚖️ Scenario Comparison")
    render_scenario_comparison(forecaster)
    
    # Sensitivity Analysis
    st.subheader("🎯 Sensitivity Analysis")
    render_sensitivity_analysis(forecaster)

def render_forecast_summary_cards(forecast_data):
    """Render forecast summary metric cards"""
    
    # Find best and worst case scenarios
    scenarios = forecast_data['forecasts']
    if not scenarios:
        st.warning("No forecast data available")
        return
    
    # Get 12-month projections for comparison
    twelve_month_results = {}
    for scenario_name, scenario_data in scenarios.items():
        if '12_months' in scenario_data:
            twelve_month_results[scenario_name] = scenario_data['12_months']['period_totals']
    
    if twelve_month_results:
        best_scenario = max(twelve_month_results.items(), key=lambda x: x[1]['total_profit'])
        worst_scenario = min(twelve_month_results.items(), key=lambda x: x[1]['total_profit'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #28a745;">Best Case (12M)</h3>
                <h2 style="margin: 0; color: #28a745;">{best_scenario[0]}</h2>
                <p style="margin: 0;">{best_scenario[1]['total_profit']:,.0f} AED profit</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #dc3545;">Worst Case (12M)</h3>
                <h2 style="margin: 0; color: #dc3545;">{worst_scenario[0]}</h2>
                <p style="margin: 0;">{worst_scenario[1]['total_profit']:,.0f} AED profit</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_revenue = sum(data['total_revenue'] for data in twelve_month_results.values()) / len(twelve_month_results)
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #17a2b8;">Avg Revenue (12M)</h3>
                <h2 style="margin: 0; color: #17a2b8;">{avg_revenue:,.0f} AED</h2>
                <p style="margin: 0;">Across all scenarios</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_customers = sum(data['final_customers'] for data in twelve_month_results.values()) / len(twelve_month_results)
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #ffc107;">Avg Customers (12M)</h3>
                <h2 style="margin: 0; color: #ffc107;">{avg_customers:,.0f}</h2>
                <p style="margin: 0;">Projected customer base</p>
            </div>
            """, unsafe_allow_html=True)

def render_forecast_charts(forecast_data):
    """Render forecast visualization charts"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue projection chart
        render_revenue_projection_chart(forecast_data)
    
    with col2:
        # Customer growth chart  
        render_customer_growth_chart(forecast_data)
    
    # Profit comparison chart (full width)
    render_profit_comparison_chart(forecast_data)

def render_revenue_projection_chart(forecast_data):
    """Render revenue projection over time"""
    chart_data = []
    
    for scenario_name, scenario_forecasts in forecast_data['forecasts'].items():
        for period_name, period_data in scenario_forecasts.items():
            months = period_data['period_months']
            total_revenue = period_data['period_totals']['total_revenue']
            
            chart_data.append({
                'Scenario': scenario_name,
                'Months': months,
                'Revenue': total_revenue
            })
    
    if chart_data:
        df_chart = pd.DataFrame(chart_data)
        fig = px.line(
            df_chart,
            x='Months',
            y='Revenue',
            color='Scenario',
            title='Revenue Projections by Scenario',
            markers=True
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def render_customer_growth_chart(forecast_data):
    """Render customer growth projections"""
    chart_data = []
    
    for scenario_name, scenario_forecasts in forecast_data['forecasts'].items():
        for period_name, period_data in scenario_forecasts.items():
            months = period_data['period_months']
            final_customers = period_data['period_totals']['final_customers']
            
            chart_data.append({
                'Scenario': scenario_name,
                'Months': months,
                'Customers': final_customers
            })
    
    if chart_data:
        df_chart = pd.DataFrame(chart_data)
        fig = px.bar(
            df_chart,
            x='Months',
            y='Customers',
            color='Scenario',
            title='Customer Growth Projections',
            barmode='group'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def render_profit_comparison_chart(forecast_data):
    """Render profit comparison across scenarios and periods"""
    chart_data = []
    
    for scenario_name, scenario_forecasts in forecast_data['forecasts'].items():
        for period_name, period_data in scenario_forecasts.items():
            months = period_data['period_months']
            total_profit = period_data['period_totals']['total_profit']
            profit_margin = period_data['period_totals']['profit_margin']
            
            chart_data.append({
                'Scenario': scenario_name,
                'Period': f"{months}M",
                'Profit': total_profit,
                'Margin': profit_margin
            })
    
    if chart_data:
        df_chart = pd.DataFrame(chart_data)
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            rows=1, cols=1,
            specs=[[{"secondary_y": True}]],
            subplot_titles=("Profit Projections with Margin Analysis",)
        )
        
        # Add profit bars
        for scenario in df_chart['Scenario'].unique():
            scenario_data = df_chart[df_chart['Scenario'] == scenario]
            fig.add_trace(
                go.Bar(
                    x=scenario_data['Period'],
                    y=scenario_data['Profit'],
                    name=f"{scenario} Profit",
                    yaxis='y'
                )
            )
        
        # Add margin line
        avg_margins = df_chart.groupby('Period')['Margin'].mean().reset_index()
        fig.add_trace(
            go.Scatter(
                x=avg_margins['Period'],
                y=avg_margins['Margin'],
                name='Avg Margin %',
                line=dict(color='red', width=3),
                yaxis='y2'
            )
        )
        
        fig.update_yaxes(title_text="Profit (AED)", secondary_y=False)
        fig.update_yaxes(title_text="Profit Margin (%)", secondary_y=True)
        fig.update_layout(height=500, barmode='group')
        
        st.plotly_chart(fig, use_container_width=True)

def render_forecast_tables(forecast_data, forecaster):
    """Render detailed forecast tables"""
    
    # Create comprehensive forecast DataFrame
    df_forecast = forecaster.create_forecast_dataframe(forecast_data)
    
    if not df_forecast.empty:
        # Format currency columns
        currency_cols = ['Total Revenue', 'Total Cost', 'Total Profit']
        for col in currency_cols:
            df_forecast[col] = df_forecast[col].apply(lambda x: f"{x:,.0f} AED")
        
        # Format percentage columns
        percentage_cols = ['Profit Margin (%)', 'Customer Growth (%)', 'Growth Rate', 'Retention Rate']
        for col in percentage_cols:
            if col in df_forecast.columns:
                df_forecast[col] = df_forecast[col].apply(lambda x: f"{x:.1f}%" if isinstance(x, (int, float)) else x)
        
        st.dataframe(df_forecast, use_container_width=True, hide_index=True)
        
        # Download option
        csv = df_forecast.to_csv(index=False)
        st.download_button(
            label="📥 Download Forecast Data",
            data=csv,
            file_name="24digi_forecast_data.csv",
            mime="text/csv"
        )

def render_scenario_comparison(forecaster):
    """Render scenario comparison analysis"""
    
    comparison_period = st.selectbox(
        "Select comparison period:",
        [3, 6, 9, 12],
        index=3,
        key="comparison_period"
    )
    
    comparison_data = forecaster.compare_scenarios(comparison_period)
    
    if comparison_data:
        # Create comparison DataFrame
        comparison_list = []
        for scenario, data in comparison_data.items():
            comparison_list.append({
                'Scenario': scenario,
                'Revenue': f"{data['total_revenue']:,.0f} AED",
                'Profit': f"{data['total_profit']:,.0f} AED",
                'Margin': f"{data['profit_margin']:.1f}%",
                'Customers': f"{data['final_customers']:,}",
                'Growth': f"{data['customer_growth']:.1f}%",
                'Risk Level': classify_risk_level(data['growth_rate'], data['retention_rate'])
            })
        
        df_comparison = pd.DataFrame(comparison_list)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)

def render_sensitivity_analysis(forecaster):
    """Render sensitivity analysis"""
    
    with st.spinner("🔄 Performing sensitivity analysis..."):
        sensitivity_data = forecaster.generate_sensitivity_analysis()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Growth rate sensitivity
        if sensitivity_data['growth_rate_sensitivity']:
            df_growth = pd.DataFrame(sensitivity_data['growth_rate_sensitivity'])
            fig = px.line(
                df_growth,
                x='growth_rate',
                y='total_profit',
                title='Profit Sensitivity to Growth Rate',
                labels={'growth_rate': 'Growth Rate (%)', 'total_profit': 'Total Profit (AED)'}
            )
            fig.update_traces(mode='lines+markers')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Retention rate sensitivity
        if sensitivity_data['retention_rate_sensitivity']:
            df_retention = pd.DataFrame(sensitivity_data['retention_rate_sensitivity'])
            fig = px.line(
                df_retention,
                x='retention_rate',
                y='total_profit',
                title='Profit Sensitivity to Retention Rate',
                labels={'retention_rate': 'Retention Rate (%)', 'total_profit': 'Total Profit (AED)'}
            )
            fig.update_traces(mode='lines+markers')
            st.plotly_chart(fig, use_container_width=True)

def classify_risk_level(growth_rate, retention_rate):
    """Classify risk level based on growth and retention parameters"""
    if growth_rate > 0.3 or retention_rate < 0.85:
        return "🔴 High Risk"
    elif growth_rate > 0.15 or retention_rate < 0.90:
        return "🟡 Medium Risk"
    else:
        return "🟢 Low Risk"
