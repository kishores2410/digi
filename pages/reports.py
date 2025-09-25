"""
24DIGI Reports Page
Comprehensive reporting and export functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from modules.calculator import RevenueCalculator
from modules.forecaster import Forecaster

def render(calculator: RevenueCalculator, forecaster: Forecaster):
    """Render the reports page"""
    
    st.header("📋 Comprehensive Reports")
    st.markdown("*Professional business reports and analytics exports*")
    
    # Report selection
    report_type = st.selectbox(
        "Select Report Type",
        [
            "Executive Summary",
            "Detailed Financial Report", 
            "Customer Analysis Report",
            "Forecast Report",
            "Custom Report Builder"
        ]
    )
    
    if report_type == "Executive Summary":
        render_executive_summary(calculator)
    elif report_type == "Detailed Financial Report":
        render_detailed_financial_report(calculator)
    elif report_type == "Customer Analysis Report":
        render_customer_analysis_report(calculator)
    elif report_type == "Forecast Report":
        render_forecast_report(forecaster)
    elif report_type == "Custom Report Builder":
        render_custom_report_builder(calculator, forecaster)

def render_executive_summary(calculator: RevenueCalculator):
    """Render executive summary report"""
    
    st.subheader("📊 Executive Summary Report")
    
    results = calculator.calculate_comprehensive_results()
    totals = results['totals']
    
    # Report header
    st.markdown(f"""
    ### 24DIGI Revenue Analytics
    **Executive Summary Report**
    
    *Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*
    
    ---
    """)
    
    # Key metrics overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 💰 Financial Performance
        """)
        st.metric("Total Revenue", f"{totals['total_revenue']:,.0f} AED")
        st.metric("Total Profit", f"{totals['total_profit']:,.0f} AED")
        st.metric("Profit Margin", f"{totals['profit_margin']:.1f}%")
    
    with col2:
        st.markdown("""
        #### 👥 Customer Metrics
        """)
        st.metric("Total Customers", f"{totals['total_customers']:,.0f} AED")
        st.metric("Revenue per Customer", f"{totals['revenue_per_customer']:,.0f} AED")
        st.metric("Profit per Customer", f"{totals['profit_per_customer']:,.0f} AED")
    
    with col3:
        st.markdown("""
        #### 📈 Performance Indicators
        """)
        revenue_cost_ratio = totals['total_revenue'] / totals['total_cost'] if totals['total_cost'] > 0 else 0
        st.metric("Revenue/Cost Ratio", f"{revenue_cost_ratio:.2f}x")
        
        # Market position (simplified)
        if totals['profit_margin'] > 30:
            market_position = "Strong"
        elif totals['profit_margin'] > 20:
            market_position = "Good"
        else:
            market_position = "Developing"
        
        st.metric("Market Position", market_position)
    
    # Top performing subscriptions
    st.markdown("#### 🏆 Top Performing Subscriptions")
    
    performance_ranking = calculator.get_subscription_performance_ranking()
    
    if performance_ranking:
        top_performers = []
        for item in performance_ranking[:3]:  # Top 3
            top_performers.append({
                'Rank': item['rank'],
                'Subscription': item['subscription_type'],
                'Total Profit': f"{item['total_profit']:,.0f} AED",
                'Profit Margin': f"{item['profit_margin']:.1f}%",
                'Customers': f"{item['customers']:,}"
            })
        
        df_top = pd.DataFrame(top_performers)
        st.dataframe(df_top, use_container_width=True, hide_index=True)
    
    # Executive insights
    st.markdown("#### 💡 Executive Insights")
    
    insights = []
    
    if totals['profit_margin'] > 35:
        insights.append("🎉 **Strong Profitability**: Profit margin exceeds industry standards, indicating excellent operational efficiency.")
    
    if totals['total_customers'] > 500:
        insights.append("📈 **Solid Customer Base**: Customer count demonstrates market acceptance and scalability.")
    
    if totals['revenue_per_customer'] > 4000:
        insights.append("💎 **High Customer Value**: Above-average revenue per customer indicates premium positioning.")
    
    # Add service diversification insight
    service_revenue = sum(data['revenue'] for data in results['additional_services'].values())
    if service_revenue > 0:
        service_percentage = (service_revenue / totals['total_revenue']) * 100
        if service_percentage > 20:
            insights.append(f"🚀 **Service Diversification**: Additional services contribute {service_percentage:.1f}% of revenue, reducing subscription dependency.")
    
    if insights:
        for insight in insights:
            st.success(insight)
    
    # Export options
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download Executive Summary", type="primary"):
            generate_executive_summary_export(results)
    
    with col2:
        if st.button("📧 Email Report", type="secondary"):
            st.info("Email functionality would be implemented with SMTP configuration")

def render_detailed_financial_report(calculator: RevenueCalculator):
    """Render detailed financial report"""
    
    st.subheader("💼 Detailed Financial Report")
    
    results = calculator.calculate_comprehensive_results()
    
    # Financial overview
    st.markdown("#### 📊 Financial Overview")
    
    # Create comprehensive financial table
    financial_data = []
    
    # Add subscription data
    for name, data in results['subscriptions'].items():
        financial_data.append({
            'Category': 'Subscription',
            'Item': name,
            'Customers': data['customers'],
            'Cost': data['total_cost'],
            'Revenue': data['total_revenue'],
            'Profit': data['total_profit'],
            'Margin (%)': data['profit_margin'],
            'Cost per Customer': data['cost_per_customer'],
            'Revenue per Customer': data['revenue_per_customer']
        })
    
    # Add service data
    for name, data in results['additional_services'].items():
        if data['revenue'] > 0:
            financial_data.append({
                'Category': 'Service',
                'Item': name,
                'Customers': 0,  # Services don't have direct customer counts
                'Cost': data['cost'],
                'Revenue': data['revenue'],
                'Profit': data['profit'],
                'Margin (%)': (data['profit'] / data['revenue'] * 100) if data['revenue'] > 0 else 0,
                'Cost per Customer': 0,
                'Revenue per Customer': 0
            })
    
    df_financial = pd.DataFrame(financial_data)
    
    # Format currency columns
    currency_cols = ['Cost', 'Revenue', 'Profit', 'Cost per Customer', 'Revenue per Customer']
    for col in currency_cols:
        df_financial[col] = df_financial[col].apply(lambda x: f"{x:,.0f} AED" if x != 0 else "0 AED")
    
    df_financial['Margin (%)'] = df_financial['Margin (%)'].apply(lambda x: f"{x:.1f}%" if isinstance(x, (int, float)) else x)
    
    st.dataframe(df_financial, use_container_width=True, hide_index=True)
    
    # Cost breakdown analysis
    st.markdown("#### 💸 Cost Structure Analysis")
    
    total_costs = results['totals']['total_cost']
    cost_breakdown = []
    
    for name, data in results['subscriptions'].items():
        if data['total_cost'] > 0:
            cost_percentage = (data['total_cost'] / total_costs) * 100
            cost_breakdown.append({
                'Cost Center': name,
                'Amount': data['total_cost'],
                'Percentage': cost_percentage
            })
    
    for name, data in results['additional_services'].items():
        if data['cost'] > 0:
            cost_percentage = (data['cost'] / total_costs) * 100
            cost_breakdown.append({
                'Cost Center': name,
                'Amount': data['cost'],
                'Percentage': cost_percentage
            })
    
    if cost_breakdown:
        df_costs = pd.DataFrame(cost_breakdown)
        
        fig_costs = px.pie(
            df_costs,
            values='Amount',
            names='Cost Center',
            title='Cost Distribution by Center'
        )
        st.plotly_chart(fig_costs, use_container_width=True)
    
    # Profitability analysis
    st.markdown("#### 📈 Profitability Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Profit margins comparison
        margin_data = []
        for name, data in results['subscriptions'].items():
            margin_data.append({
                'Subscription': name.replace(' - ', '\n'),  # Line break for better display
                'Profit Margin': data['profit_margin']
            })
        
        if margin_data:
            df_margins = pd.DataFrame(margin_data)
            fig_margins = px.bar(
                df_margins,
                x='Subscription',
                y='Profit Margin',
                title='Profit Margins by Subscription',
                color='Profit Margin',
                color_continuous_scale='RdYlGn'
            )
            fig_margins.update_layout(height=400)
            st.plotly_chart(fig_margins, use_container_width=True)
    
    with col2:
        # Revenue vs Profit scatter
        scatter_data = []
        for name, data in results['subscriptions'].items():
            scatter_data.append({
                'Subscription': name.split(' - ')[0],  # Just the type
                'Revenue': data['total_revenue'],
                'Profit': data['total_profit'],
                'Customers': data['customers']
            })
        
        if scatter_data:
            df_scatter = pd.DataFrame(scatter_data)
            fig_scatter = px.scatter(
                df_scatter,
                x='Revenue',
                y='Profit',
                size='Customers',
                color='Subscription',
                title='Revenue vs Profit by Subscription Type',
                hover_data=['Customers']
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

def render_customer_analysis_report(calculator: RevenueCalculator):
    """Render customer analysis report"""
    
    st.subheader("👥 Customer Analysis Report")
    
    results = calculator.calculate_comprehensive_results()
    
    # Customer distribution analysis
    st.markdown("#### 📊 Customer Distribution")
    
    customer_data = []
    total_customers = results['totals']['total_customers']
    
    for name, data in results['subscriptions'].items():
        if data['customers'] > 0:
            customer_percentage = (data['customers'] / total_customers) * 100
            
            customer_data.append({
                'Subscription Type': name,
                'Customers': data['customers'],
                'Percentage': customer_percentage,
                'Revenue per Customer': data['revenue_per_customer'],
                'Profit per Customer': data['total_profit'] / data['customers'],
                'Total Revenue': data['total_revenue']
            })
    
    df_customers = pd.DataFrame(customer_data)
    
    # Customer metrics table
    df_display = df_customers.copy()
    df_display['Revenue per Customer'] = df_display['Revenue per Customer'].apply(lambda x: f"{x:,.0f} AED")
    df_display['Profit per Customer'] = df_display['Profit per Customer'].apply(lambda x: f"{x:,.0f} AED")
    df_display['Total Revenue'] = df_display['Total Revenue'].apply(lambda x: f"{x:,.0f} AED")
    df_display['Percentage'] = df_display['Percentage'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Customer value analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer count by subscription
        fig_customers = px.pie(
            df_customers,
            values='Customers',
            names='Subscription Type',
            title='Customer Distribution by Subscription Type'
        )
        st.plotly_chart(fig_customers, use_container_width=True)
    
    with col2:
        # Customer value segments
        fig_value = px.scatter(
            df_customers,
            x='Customers',
            y='Revenue per Customer',
            size='Total Revenue',
            color='Subscription Type',
            title='Customer Value Analysis',
            hover_data=['Total Revenue']
        )
        st.plotly_chart(fig_value, use_container_width=True)

def render_forecast_report(forecaster: Forecaster):
    """Render forecast report"""
    
    st.subheader("🔮 Forecast Report")
    
    # Forecast parameters
    col1, col2 = st.columns(2)
    
    with col1:
        forecast_periods = st.multiselect(
            "Select forecast periods (months)",
            [3, 6, 9, 12, 18, 24],
            default=[6, 12],
            key="forecast_report_periods"
        )
    
    with col2:
        forecast_scenarios = st.multiselect(
            "Select scenarios",
            ['Conservative', 'Moderate', 'Aggressive', 'Optimistic'],
            default=['Conservative', 'Moderate', 'Aggressive'],
            key="forecast_report_scenarios"
        )
    
    if forecast_periods and forecast_scenarios:
        # Generate forecast
        with st.spinner("🔄 Generating forecast report..."):
            forecast_data = forecaster.generate_forecast(forecast_periods, forecast_scenarios)
        
        # Forecast summary table
        st.markdown("#### 📊 Forecast Summary")
        
        df_forecast = forecaster.create_forecast_dataframe(forecast_data)
        
        if not df_forecast.empty:
            # Format for display
            df_display = df_forecast.copy()
            
            # Format currency columns
            currency_cols = ['Total Revenue', 'Total Cost', 'Total Profit']
            for col in currency_cols:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f} AED")
            
            # Format percentage columns
            percentage_cols = ['Profit Margin (%)', 'Customer Growth (%)']
            for col in percentage_cols:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Forecast visualizations
        st.markdown("#### 📈 Forecast Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue projections
            if not df_forecast.empty:
                fig_revenue = px.line(
                    df_forecast,
                    x='Period (Months)',
                    y='Total Revenue',
                    color='Scenario',
                    title='Revenue Projections',
                    markers=True
                )
                st.plotly_chart(fig_revenue, use_container_width=True)
        
        with col2:
            # Customer growth projections
            if not df_forecast.empty:
                fig_customers = px.bar(
                    df_forecast,
                    x='Period (Months)',
                    y='Final Customers',
                    color='Scenario',
                    title='Customer Growth Projections',
                    barmode='group'
                )
                st.plotly_chart(fig_customers, use_container_width=True)
        
        # Scenario comparison
        st.markdown("#### ⚖️ Scenario Comparison")
        
        comparison_period = st.selectbox("Compare scenarios for period:", forecast_periods, key="comparison_select")
        
        if comparison_period:
            comparison_data = forecaster.compare_scenarios(comparison_period)
            
            comparison_list = []
            for scenario, data in comparison_data.items():
                comparison_list.append({
                    'Scenario': scenario,
                    'Revenue': f"{data['total_revenue']:,.0f} AED",
                    'Profit': f"{data['total_profit']:,.0f} AED",
                    'Margin': f"{data['profit_margin']:.1f}%",
                    'Customers': f"{data['final_customers']:,}",
                    'Growth': f"{data['customer_growth']:.1f}%"
                })
            
            df_comparison = pd.DataFrame(comparison_list)
            st.dataframe(df_comparison, use_container_width=True, hide_index=True)

def render_custom_report_builder(calculator: RevenueCalculator, forecaster: Forecaster):
    """Render custom report builder"""
    
    st.subheader("🛠️ Custom Report Builder")
    st.markdown("*Build personalized reports with selected components*")
    
    # Report configuration
    st.markdown("#### ⚙️ Report Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_name = st.text_input("Report Name", value="Custom Business Report")
        report_description = st.text_area("Report Description", value="Custom analysis report generated by 24DIGI Analytics Platform")
    
    with col2:
        include_executive_summary = st.checkbox("Include Executive Summary", value=True)
        include_financial_details = st.checkbox("Include Financial Details", value=True)
        include_customer_analysis = st.checkbox("Include Customer Analysis", value=False)
        include_forecasting = st.checkbox("Include Forecasting", value=False)
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        date_range = st.date_input("Report Period", value=[datetime.now().date()])
        currency_format = st.selectbox("Currency Format", ["AED", "EUR (€)", "GBP (£)"], index=0)
        decimal_places = st.selectbox("Decimal Places", [0, 1, 2], index=0)
    
    # Generate custom report
    if st.button("📋 Generate Custom Report", type="primary"):
        st.markdown("---")
        st.markdown(f"# {report_name}")
        st.markdown(f"*{report_description}*")
        st.markdown(f"**Generated on:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        st.markdown("---")
        
        # Include selected components
        if include_executive_summary:
            st.markdown("## Executive Summary")
            render_custom_executive_section(calculator)
            st.markdown("---")
        
        if include_financial_details:
            st.markdown("## Financial Analysis")
            render_custom_financial_section(calculator)
            st.markdown("---")
        
        if include_customer_analysis:
            st.markdown("## Customer Analysis")
            render_custom_customer_section(calculator)
            st.markdown("---")
        
        if include_forecasting:
            st.markdown("## Forecasting Analysis")
            render_custom_forecast_section(forecaster)
            st.markdown("---")
        
        # Report footer
        st.markdown("## Report Summary")
        st.info("This custom report was generated using 24DIGI Analytics Platform. All data is based on current configuration and inputs.")
        
        # Export options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export as CSV"):
                generate_csv_export(calculator)
        
        with col2:
            if st.button("📊 Export Charts"):
                st.info("Chart export functionality would be implemented with plotly export features")
        
        with col3:
            if st.button("📧 Share Report"):
                st.info("Report sharing functionality would be implemented with email/link sharing")

def render_custom_executive_section(calculator: RevenueCalculator):
    """Render custom executive summary section"""
    
    results = calculator.calculate_comprehensive_results()
    totals = results['totals']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Revenue", f"{totals['total_revenue']:,.0f} AED")
        st.metric("Total Customers", f"{totals['total_customers']:,.0f} AED")
    
    with col2:
        st.metric("Total Profit", f"{totals['total_profit']:,.0f} AED")
        st.metric("Profit Margin", f"{totals['profit_margin']:.1f}%")
    
    with col3:
        st.metric("Revenue per Customer", f"{totals['revenue_per_customer']:,.0f} AED")
        revenue_cost_ratio = totals['total_revenue'] / totals['total_cost'] if totals['total_cost'] > 0 else 0
        st.metric("Revenue/Cost Ratio", f"{revenue_cost_ratio:.2f}x")

def render_custom_financial_section(calculator: RevenueCalculator):
    """Render custom financial analysis section"""
    
    results = calculator.calculate_comprehensive_results()
    
    # Revenue breakdown
    revenue_data = []
    for name, data in results['subscriptions'].items():
        revenue_data.append({
            'Category': name,
            'Revenue': data['total_revenue'],
            'Profit': data['total_profit'],
            'Margin': data['profit_margin']
        })
    
    df_revenue = pd.DataFrame(revenue_data)
    
    if not df_revenue.empty:
        fig = px.bar(
            df_revenue,
            x='Category',
            y=['Revenue', 'Profit'],
            title='Revenue and Profit by Category',
            barmode='group'
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

def render_custom_customer_section(calculator: RevenueCalculator):
    """Render custom customer analysis section"""
    
    results = calculator.calculate_comprehensive_results()
    
    customer_data = []
    for name, data in results['subscriptions'].items():
        if data['customers'] > 0:
            customer_data.append({
                'Subscription': name,
                'Customers': data['customers'],
                'Revenue per Customer': data['revenue_per_customer']
            })
    
    if customer_data:
        df_customers = pd.DataFrame(customer_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(
                df_customers,
                values='Customers',
                names='Subscription',
                title='Customer Distribution'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            fig_bar = px.bar(
                df_customers,
                x='Subscription',
                y='Revenue per Customer',
                title='Revenue per Customer by Subscription'
            )
            fig_bar.update_xaxes(tickangle=45)
            st.plotly_chart(fig_bar, use_container_width=True)

def render_custom_forecast_section(forecaster: Forecaster):
    """Render custom forecast analysis section"""
    
    # Simple 12-month forecast for all scenarios
    forecast_data = forecaster.generate_forecast([12], ['Conservative', 'Moderate', 'Aggressive'])
    
    if forecast_data:
        df_forecast = forecaster.create_forecast_dataframe(forecast_data)
        
        if not df_forecast.empty:
            # Show summary table
            summary_data = []
            for scenario in ['Conservative', 'Moderate', 'Aggressive']:
                scenario_data = df_forecast[df_forecast['Scenario'] == scenario]
                if not scenario_data.empty:
                    row = scenario_data.iloc[0]
                    summary_data.append({
                        'Scenario': scenario,
                        'Projected Revenue': f"{row['Total Revenue']:,.0f} AED",
                        'Projected Profit': f"{row['Total Profit']:,.0f} AED",
                        'Projected Customers': f"{row['Final Customers']:,}"
                    })
            
            if summary_data:
                df_summary = pd.DataFrame(summary_data)
                st.dataframe(df_summary, use_container_width=True, hide_index=True)

def generate_executive_summary_export(results):
    """Generate executive summary export data"""
    
    # Create export data
    export_data = {
        'report_type': 'Executive Summary',
        'generated_at': datetime.now().isoformat(),
        'company': '24DIGI',
        'totals': results['totals'],
        'subscriptions': results['subscriptions'],
        'additional_services': results['additional_services']
    }
    
    # Convert to JSON for download
    json_str = json.dumps(export_data, indent=2, default=str)
    
    st.download_button(
        label="💾 Download Executive Summary JSON",
        data=json_str,
        file_name=f"24digi_executive_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json"
    )

def generate_csv_export(calculator: RevenueCalculator):
    """Generate CSV export of calculation results"""
    
    results = calculator.calculate_comprehensive_results()
    
    # Create comprehensive CSV data
    csv_data = []
    
    # Add subscription data
    for name, data in results['subscriptions'].items():
        csv_data.append({
            'Category': 'Subscription',
            'Name': name,
            'Customers': data['customers'],
            'Cost': data['total_cost'],
            'Revenue': data['total_revenue'],
            'Profit': data['total_profit'],
            'Margin_Percent': data['profit_margin'],
            'Cost_Per_Customer': data['cost_per_customer'],
            'Revenue_Per_Customer': data['revenue_per_customer']
        })
    
    # Add service data
    for name, data in results['additional_services'].items():
        csv_data.append({
            'Category': 'Service',
            'Name': name,
            'Customers': 0,
            'Cost': data['cost'],
            'Revenue': data['revenue'],
            'Profit': data['profit'],
            'Margin_Percent': (data['profit'] / data['revenue'] * 100) if data['revenue'] > 0 else 0,
            'Cost_Per_Customer': 0,
            'Revenue_Per_Customer': 0
        })
    
    # Add totals row
    totals = results['totals']
    csv_data.append({
        'Category': 'TOTAL',
        'Name': 'All Services',
        'Customers': totals['total_customers'],
        'Cost': totals['total_cost'],
        'Revenue': totals['total_revenue'],
        'Profit': totals['total_profit'],
        'Margin_Percent': totals['profit_margin'],
        'Cost_Per_Customer': totals['cost_per_customer'],
        'Revenue_Per_Customer': totals['revenue_per_customer']
    })
    
    df_export = pd.DataFrame(csv_data)
    csv_string = df_export.to_csv(index=False)
    
    st.download_button(
        label="📥 Download CSV Report",
        data=csv_string,
        file_name=f"24digi_financial_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )
    
    st.success("✅ CSV export ready for download!")
