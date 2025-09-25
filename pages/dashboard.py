"""
24DIGI Dashboard Page
Executive dashboard with key metrics and overview
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from modules.data_manager import DataManager
from modules.calculator import RevenueCalculator

def render(data_manager: DataManager, calculator: RevenueCalculator):
    """Render the dashboard page"""
    
    st.header("📊 Executive Dashboard")
    st.markdown("*Real-time business performance overview*")
    
    # Calculate current results
    results = calculator.calculate_comprehensive_results()
    totals = results['totals']
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #1e3c72;">Total Revenue</h3>
            <h1 style="margin: 0; color: #2a5298;">{:,.0f} AED</h1>
            <p style="margin: 0; color: #666;">{:,.0f} AED per customer</p>
        </div>
        """.format(totals['total_revenue'], totals['revenue_per_customer']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #1e3c72;">Total Profit</h3>
            <h1 style="margin: 0; color: #28a745;">{:,.0f} AED</h1>
            <p style="margin: 0; color: #666;">{:.1f}% margin</p>
        </div>
        """.format(totals['total_profit'], totals['profit_margin']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #1e3c72;">Total Customers</h3>
            <h1 style="margin: 0; color: #17a2b8;">{:,}</h1>
            <p style="margin: 0; color: #666;">Active subscribers</p>
        </div>
        """.format(int(totals['total_customers'])), unsafe_allow_html=True)
    
    with col4:
        cost_recovery_ratio = (totals['total_revenue'] / totals['total_cost']) if totals['total_cost'] > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #1e3c72;">Revenue Multiple</h3>
            <h1 style="margin: 0; color: #ffc107;">{:.2f}x</h1>
            <p style="margin: 0; color: #666;">Revenue/Cost ratio</p>
        </div>
        """.format(cost_recovery_ratio), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue Distribution Pie Chart
        revenue_data = []
        for name, data in results['subscriptions'].items():
            revenue_data.append({'Category': name, 'Revenue': data['total_revenue']})
        
        for name, data in results['additional_services'].items():
            if data['revenue'] > 0:
                revenue_data.append({'Category': name, 'Revenue': data['revenue']})
        
        if revenue_data:
            df_revenue = pd.DataFrame(revenue_data)
            fig_pie = px.pie(
                df_revenue, 
                values='Revenue', 
                names='Category',
                title="Revenue Distribution",
                color_discrete_sequence=['#1e3c72', '#2a5298', '#3d5aa8', '#5068b8', '#6377c8']
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400, showlegend=True, legend=dict(orientation="v", x=1.05))
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Profit by Subscription Type
        profit_data = []
        for name, data in results['subscriptions'].items():
            profit_data.append({
                'Subscription': name.split(' - ')[0],  # Get just the type
                'Duration': name.split(' - ')[1] if ' - ' in name else '',
                'Profit': data['total_profit'],
                'Margin': data['profit_margin']
            })
        
        if profit_data:
            df_profit = pd.DataFrame(profit_data)
            fig_bar = px.bar(
                df_profit,
                x='Subscription',
                y='Profit',
                color='Duration',
                title="Profit by Subscription Type",
                color_discrete_sequence=['#1e3c72', '#2a5298']
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Detailed Performance Table
    st.subheader("📈 Subscription Performance Analysis")
    
    # Create performance DataFrame
    performance_data = []
    for name, data in results['subscriptions'].items():
        performance_data.append({
            'Subscription Type': name,
            'Customers': data['customers'],
            'Revenue per Customer': f"{data['revenue_per_customer']:,.0f} AED",
            'Total Revenue': f"{data['total_revenue']:,.0f} AED",
            'Total Profit': f"{data['total_profit']:,.0f} AED",
            'Profit Margin': f"{data['profit_margin']:.1f}%",
            'Renewals': data['renewals']
        })
    
    if performance_data:
        df_performance = pd.DataFrame(performance_data)
        
        # Style the dataframe
        st.dataframe(
            df_performance,
            use_container_width=True,
            hide_index=True
        )
    
    # Additional Services Summary
    st.subheader("🛠️ Additional Services Performance")
    
    services_data = []
    for name, data in results['additional_services'].items():
        if data['revenue'] > 0:  # Only show services with revenue
            services_data.append({
                'Service': name,
                'Revenue': f"{data['revenue']:,.0f} AED",
                'Cost': f"{data['cost']:,.0f} AED",
                'Profit': f"{data['profit']:,.0f} AED",
                'Margin': f"{(data['profit']/data['revenue']*100) if data['revenue'] > 0 else 0:.1f}%"
            })
    
    if services_data:
        df_services = pd.DataFrame(services_data)
        st.dataframe(df_services, use_container_width=True, hide_index=True)
    else:
        st.info("No additional services configured with revenue.")
    
    # Business Intelligence Insights
    st.subheader("🧠 Business Intelligence Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💡 Key Insights")
        
        # Find best performing subscription
        best_subscription = max(results['subscriptions'].items(), key=lambda x: x[1]['total_profit'], default=None)
        if best_subscription:
            st.success(f"**Top Performer:** {best_subscription[0]} generates {best_subscription[1]['total_profit']:,.0f} AED profit")
        
        # Find highest margin subscription
        highest_margin = max(results['subscriptions'].items(), key=lambda x: x[1]['profit_margin'], default=None)
        if highest_margin:
            st.info(f"**Highest Margin:** {highest_margin[0]} has {highest_margin[1]['profit_margin']:.1f}% profit margin")
        
        # Customer value insights
        if totals['total_customers'] > 0:
            st.warning(f"**Customer LTV:** Average customer generates {totals['profit_per_customer']:,.0f} AED profit")
    
    with col2:
        st.markdown("#### 📊 Performance Metrics")
        
        # Create gauge chart for overall health
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = totals['profit_margin'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Profit Margin (%)"},
            delta = {'reference': 25, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge = {
                'axis': {'range': [None, 50]},
                'bar': {'color': "#1e3c72"},
                'steps': [
                    {'range': [0, 15], 'color': "lightgray"},
                    {'range': [15, 30], 'color': "yellow"},
                    {'range': [30, 50], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 40
                }
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Growth Opportunities
    st.subheader("🚀 Growth Opportunities")
    
    opportunities = []
    
    # Identify underperforming subscriptions
    avg_margin = sum(data['profit_margin'] for data in results['subscriptions'].values()) / len(results['subscriptions']) if results['subscriptions'] else 0
    
    for name, data in results['subscriptions'].items():
        if data['profit_margin'] < avg_margin * 0.8:  # 20% below average
            opportunities.append(f"**{name}** has below-average margin ({data['profit_margin']:.1f}% vs {avg_margin:.1f}% average)")
    
    # Identify low customer segments
    total_customers = sum(data['customers'] for data in results['subscriptions'].values())
    avg_customers_per_type = total_customers / len(results['subscriptions']) if results['subscriptions'] else 0
    
    for name, data in results['subscriptions'].items():
        if data['customers'] < avg_customers_per_type * 0.5:  # 50% below average
            opportunities.append(f"**{name}** has low customer count ({data['customers']} vs {avg_customers_per_type:.0f} average)")
    
    if opportunities:
        for opportunity in opportunities[:3]:  # Show top 3
            st.warning(opportunity)
    else:
        st.success("🎉 All subscription types are performing well!")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔧 Optimize Pricing", type="primary"):
            st.info("Navigate to Pricing Configuration tab to adjust pricing strategies")
    
    with col2:
        if st.button("📈 View Forecasting", type="primary"):
            st.info("Navigate to Forecasting tab for growth projections")
    
    with col3:
        if st.button("📋 Generate Report", type="primary"):
            st.info("Navigate to Reports tab for detailed analysis")
