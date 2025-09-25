"""
24DIGI Analytics Page
Advanced analytics and business intelligence
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.data_manager import DataManager
from modules.calculator import RevenueCalculator

def render(data_manager: DataManager, calculator: RevenueCalculator):
    """Render the analytics page"""
    
    st.header("📈 Advanced Analytics")
    st.markdown("*Deep dive into business performance and intelligence*")
    
    # Calculate current results
    results = calculator.calculate_comprehensive_results()
    
    # Key Performance Indicators
    render_kpi_section(results)
    
    # Revenue Analysis
    render_revenue_analysis(results)
    
    # Customer Analysis  
    render_customer_analysis(results)
    
    # Profitability Analysis
    render_profitability_analysis(results)
    
    # Business Intelligence
    render_business_intelligence(results, calculator)

def render_kpi_section(results):
    """Render Key Performance Indicators"""
    
    st.subheader("🎯 Key Performance Indicators")
    
    totals = results['totals']
    
    # Main KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics = [
        ("Total Revenue", f"{totals['total_revenue']:,.0f} AED", "💰"),
        ("Total Profit", f"{totals['total_profit']:,.0f} AED", "📈"),
        ("Profit Margin", f"{totals['profit_margin']:.1f}%", "📊"),
        ("Total Customers", f"{totals['total_customers']:,.0f} AED", "👥"),
        ("Avg Revenue/Customer", f"{totals['revenue_per_customer']:,.0f} AED", "💎")
    ]
    
    for i, (title, value, icon) in enumerate(metrics):
        with [col1, col2, col3, col4, col5][i]:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="margin: 0; color: #666; font-size: 0.9rem;">{icon} {title}</h3>
                <h1 style="margin: 0.5rem 0 0 0; color: #1e3c72; font-size: 1.5rem;">{value}</h1>
            </div>
            """, unsafe_allow_html=True)
    
    # Secondary KPIs
    st.markdown("#### 📋 Additional Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cost per Customer", f"{totals['cost_per_customer']:,.0f} AED")
        st.metric("Profit per Customer", f"{totals['profit_per_customer']:,.0f} AED")
    
    with col2:
        revenue_cost_ratio = totals['total_revenue'] / totals['total_cost'] if totals['total_cost'] > 0 else 0
        st.metric("Revenue/Cost Ratio", f"{revenue_cost_ratio:.2f}x")
        
        # Calculate break-even point
        fixed_costs = totals['total_cost']  # Simplified assumption
        break_even_customers = fixed_costs / totals['profit_per_customer'] if totals['profit_per_customer'] > 0 else 0
        st.metric("Break-even Customers", f"{break_even_customers:,.0f} AED")
    
    with col3:
        # Market penetration (assuming total addressable market)
        estimated_tam = 10000  # Assume 10K potential customers
        market_penetration = (totals['total_customers'] / estimated_tam) * 100
        st.metric("Market Penetration", f"{market_penetration:.1f}%")
        
        # Customer acquisition cost (simplified)
        total_marketing_cost = totals['total_cost'] * 0.15  # Assume 15% of costs for marketing
        cac = total_marketing_cost / totals['total_customers'] if totals['total_customers'] > 0 else 0
        st.metric("Est. Customer Acq. Cost", f"{cac:.0f} AED")
    
    with col4:
        # Customer Lifetime Value (simplified 12 month projection)
        clv = totals['revenue_per_customer'] * 4  # Assume quarterly billing for 1 year
        st.metric("Est. Customer LTV (12M)", f"{clv:,.0f} AED")
        
        # LTV/CAC Ratio
        ltv_cac_ratio = clv / cac if cac > 0 else 0
        st.metric("LTV/CAC Ratio", f"{ltv_cac_ratio:.1f}x")

def render_revenue_analysis(results):
    """Render detailed revenue analysis"""
    
    st.subheader("💰 Revenue Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue distribution pie chart
        revenue_data = []
        
        # Add subscription revenue
        for name, data in results['subscriptions'].items():
            revenue_data.append({
                'Category': name,
                'Revenue': data['total_revenue'],
                'Type': 'Subscription'
            })
        
        # Add service revenue
        for name, data in results['additional_services'].items():
            if data['revenue'] > 0:
                revenue_data.append({
                    'Category': name,
                    'Revenue': data['revenue'],
                    'Type': 'Service'
                })
        
        if revenue_data:
            df_revenue = pd.DataFrame(revenue_data)
            
            fig_pie = px.pie(
                df_revenue,
                values='Revenue',
                names='Category',
                title='Revenue Distribution by Category',
                color='Type',
                color_discrete_map={'Subscription': '#1e3c72', 'Service': '#2a5298'}
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Revenue by subscription type
        subscription_data = []
        for name, data in results['subscriptions'].items():
            parts = name.split(' - ')
            sub_type = parts[0] if len(parts) > 0 else name
            duration = parts[1] if len(parts) > 1 else 'Unknown'
            
            subscription_data.append({
                'Type': sub_type,
                'Duration': duration,
                'Revenue': data['total_revenue']
            })
        
        if subscription_data:
            df_subs = pd.DataFrame(subscription_data)
            
            fig_bar = px.bar(
                df_subs,
                x='Type',
                y='Revenue',
                color='Duration',
                title='Revenue by Subscription Type & Duration',
                color_discrete_sequence=['#1e3c72', '#2a5298']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Revenue trends analysis (waterfall chart simulation)
    st.markdown("#### 🌊 Revenue Waterfall Analysis")
    
    waterfall_data = []
    cumulative = 0
    
    # Add subscription revenues
    for name, data in results['subscriptions'].items():
        waterfall_data.append({
            'Category': name,
            'Value': data['total_revenue'],
            'Cumulative': cumulative + data['total_revenue'],
            'Type': 'Subscription'
        })
        cumulative += data['total_revenue']
    
    # Add service revenues
    for name, data in results['additional_services'].items():
        if data['revenue'] > 0:
            waterfall_data.append({
                'Category': name,
                'Value': data['revenue'],
                'Cumulative': cumulative + data['revenue'],
                'Type': 'Service'
            })
            cumulative += data['revenue']
    
    if waterfall_data:
        df_waterfall = pd.DataFrame(waterfall_data)
        
        fig_waterfall = go.Figure()
        
        # Add bars for each category
        for i, row in df_waterfall.iterrows():
            fig_waterfall.add_trace(go.Bar(
                x=[row['Category']],
                y=[row['Value']],
                name=row['Category'],
                text=f"{row['Value']:,.0f} AED",
                textposition='auto',
                marker_color='#1e3c72' if row['Type'] == 'Subscription' else '#2a5298'
            ))
        
        fig_waterfall.update_layout(
            title='Revenue Contribution by Category',
            showlegend=False,
            height=400
        )
        fig_waterfall.update_xaxes(tickangle=45)
        
        st.plotly_chart(fig_waterfall, use_container_width=True)

def render_customer_analysis(results):
    """Render customer analysis section"""
    
    st.subheader("👥 Customer Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer distribution by subscription type
        customer_data = []
        for name, data in results['subscriptions'].items():
            if data['customers'] > 0:
                parts = name.split(' - ')
                sub_type = parts[0] if len(parts) > 0 else name
                duration = parts[1] if len(parts) > 1 else 'Unknown'
                
                customer_data.append({
                    'Subscription Type': sub_type,
                    'Duration': duration,
                    'Customers': data['customers'],
                    'Revenue per Customer': data['revenue_per_customer']
                })
        
        if customer_data:
            df_customers = pd.DataFrame(customer_data)
            
            fig_bubble = px.scatter(
                df_customers,
                x='Customers',
                y='Revenue per Customer',
                size='Customers',
                color='Subscription Type',
                title='Customer Count vs Revenue per Customer',
                hover_data=['Duration']
            )
            st.plotly_chart(fig_bubble, use_container_width=True)
    
    with col2:
        # Customer value segments
        if customer_data:
            # Calculate customer segments
            total_customers = sum(item['Customers'] for item in customer_data)
            total_revenue = sum(item['Customers'] * item['Revenue per Customer'] for item in customer_data)
            
            segments = []
            for item in customer_data:
                revenue_contribution = (item['Customers'] * item['Revenue per Customer']) / total_revenue * 100
                customer_percentage = item['Customers'] / total_customers * 100
                
                segments.append({
                    'Segment': f"{item['Subscription Type']} {item['Duration']}",
                    'Customer %': customer_percentage,
                    'Revenue %': revenue_contribution
                })
            
            df_segments = pd.DataFrame(segments)
            
            fig_segments = px.scatter(
                df_segments,
                x='Customer %',
                y='Revenue %',
                size='Revenue %',
                title='Customer Segments: % of Customers vs % of Revenue',
                text='Segment'
            )
            fig_segments.update_traces(textposition='top center')
            fig_segments.add_shape(
                type="line",
                x0=0, y0=0, x1=100, y1=100,
                line=dict(color="red", dash="dash"),
                opacity=0.5
            )
            st.plotly_chart(fig_segments, use_container_width=True)
    
    # Customer metrics table
    st.markdown("#### 📊 Customer Metrics by Subscription")
    
    if customer_data:
        df_customer_metrics = pd.DataFrame(customer_data)
        
        # Add calculated metrics
        df_customer_metrics['Total Revenue'] = df_customer_metrics['Customers'] * df_customer_metrics['Revenue per Customer']
        df_customer_metrics['Market Share (Customers)'] = (df_customer_metrics['Customers'] / df_customer_metrics['Customers'].sum() * 100).round(1)
        df_customer_metrics['Revenue Share'] = (df_customer_metrics['Total Revenue'] / df_customer_metrics['Total Revenue'].sum() * 100).round(1)
        
        # Format for display
        df_display = df_customer_metrics.copy()
        df_display['Revenue per Customer'] = df_display['Revenue per Customer'].apply(lambda x: f"{x:,.0f} AED")
        df_display['Total Revenue'] = df_display['Total Revenue'].apply(lambda x: f"{x:,.0f} AED")
        df_display['Market Share (Customers)'] = df_display['Market Share (Customers)'].apply(lambda x: f"{x}%")
        df_display['Revenue Share'] = df_display['Revenue Share'].apply(lambda x: f"{x}%")
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)

def render_profitability_analysis(results):
    """Render profitability analysis section"""
    
    st.subheader("💹 Profitability Analysis")
    
    # Profit margin comparison
    col1, col2 = st.columns(2)
    
    with col1:
        # Profit margins by subscription
        profit_data = []
        for name, data in results['subscriptions'].items():
            profit_data.append({
                'Subscription': name,
                'Profit Margin': data['profit_margin'],
                'Total Profit': data['total_profit']
            })
        
        if profit_data:
            df_profit = pd.DataFrame(profit_data)
            
            fig_margin = px.bar(
                df_profit,
                x='Subscription',
                y='Profit Margin',
                title='Profit Margins by Subscription Type',
                color='Profit Margin',
                color_continuous_scale='RdYlGn'
            )
            fig_margin.update_xaxes(tickangle=45)
            fig_margin.update_layout(height=400)
            st.plotly_chart(fig_margin, use_container_width=True)
    
    with col2:
        # Cost structure analysis
        cost_data = []
        for name, data in results['subscriptions'].items():
            if data['customers'] > 0:
                cost_data.append({
                    'Category': name,
                    'Cost': data['total_cost'],
                    'Revenue': data['total_revenue']
                })
        
        # Add service costs
        for name, data in results['additional_services'].items():
            if data['cost'] > 0:
                cost_data.append({
                    'Category': name,
                    'Cost': data['cost'],
                    'Revenue': data['revenue']
                })
        
        if cost_data:
            df_cost = pd.DataFrame(cost_data)
            
            fig_cost = px.bar(
                df_cost,
                x='Category',
                y=['Cost', 'Revenue'],
                title='Cost vs Revenue by Category',
                barmode='group',
                color_discrete_map={'Cost': '#dc3545', 'Revenue': '#28a745'}
            )
            fig_cost.update_xaxes(tickangle=45)
            fig_cost.update_layout(height=400)
            st.plotly_chart(fig_cost, use_container_width=True)
    
    # Profitability heatmap
    st.markdown("#### 🔥 Profitability Heatmap")
    
    # Create profitability matrix
    heatmap_data = []
    for name, data in results['subscriptions'].items():
        parts = name.split(' - ')
        sub_type = parts[0] if len(parts) > 0 else name
        duration = parts[1] if len(parts) > 1 else 'Unknown'
        
        heatmap_data.append({
            'Subscription Type': sub_type,
            'Duration': duration,
            'Profit Margin': data['profit_margin'],
            'Total Profit': data['total_profit'],
            'Customers': data['customers']
        })
    
    if heatmap_data:
        df_heatmap = pd.DataFrame(heatmap_data)
        
        # Create pivot table for heatmap
        pivot_margin = df_heatmap.pivot(index='Subscription Type', columns='Duration', values='Profit Margin')
        pivot_profit = df_heatmap.pivot(index='Subscription Type', columns='Duration', values='Total Profit')
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not pivot_margin.empty:
                fig_heatmap1 = px.imshow(
                    pivot_margin,
                    title='Profit Margin Heatmap (%)',
                    color_continuous_scale='RdYlGn',
                    aspect='auto'
                )
                st.plotly_chart(fig_heatmap1, use_container_width=True)
        
        with col2:
            if not pivot_profit.empty:
                fig_heatmap2 = px.imshow(
                    pivot_profit,
                    title='Total Profit Heatmap (AED)',
                    color_continuous_scale='Blues',
                    aspect='auto'
                )
                st.plotly_chart(fig_heatmap2, use_container_width=True)

def render_business_intelligence(results, calculator):
    """Render business intelligence insights"""
    
    st.subheader("🧠 Business Intelligence Insights")
    
    # Performance ranking
    performance_ranking = calculator.get_subscription_performance_ranking()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Performance Ranking")
        
        if performance_ranking:
            ranking_data = []
            for item in performance_ranking:
                ranking_data.append({
                    'Rank': item['rank'],
                    'Subscription': item['subscription_type'],
                    'Profit': f"{item['total_profit']:,.0f} AED",
                    'Margin': f"{item['profit_margin']:.1f}%",
                    'Customers': f"{item['customers']:,}",
                    'Performance Score': f"{item['score']:.0f}"
                })
            
            df_ranking = pd.DataFrame(ranking_data)
            st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 💡 Key Insights")
        
        # Generate insights
        insights = generate_business_insights(results, performance_ranking)
        
        for insight in insights:
            if insight['type'] == 'success':
                st.success(insight['message'])
            elif insight['type'] == 'warning':
                st.warning(insight['message'])
            elif insight['type'] == 'info':
                st.info(insight['message'])
    
    # Recommendations
    st.markdown("#### 🎯 Strategic Recommendations")
    
    recommendations = generate_recommendations(results, performance_ranking)
    
    for i, rec in enumerate(recommendations, 1):
        with st.expander(f"💼 Recommendation {i}: {rec['title']}"):
            st.markdown(f"**Priority:** {rec['priority']}")
            st.markdown(f"**Impact:** {rec['impact']}")
            st.markdown(f"**Description:** {rec['description']}")
            if rec['actions']:
                st.markdown("**Suggested Actions:**")
                for action in rec['actions']:
                    st.markdown(f"- {action}")

def generate_business_insights(results, performance_ranking):
    """Generate automated business insights"""
    insights = []
    
    totals = results['totals']
    
    # Profit margin insights
    if totals['profit_margin'] > 40:
        insights.append({
            'type': 'success',
            'message': f"🎉 Excellent profit margin of {totals['profit_margin']:.1f}% indicates strong pricing power and operational efficiency."
        })
    elif totals['profit_margin'] > 25:
        insights.append({
            'type': 'info',
            'message': f"✅ Healthy profit margin of {totals['profit_margin']:.1f}% provides good financial stability."
        })
    else:
        insights.append({
            'type': 'warning',
            'message': f"⚠️ Profit margin of {totals['profit_margin']:.1f}% may indicate opportunities for cost optimization or pricing adjustments."
        })
    
    # Customer concentration insights
    if performance_ranking:
        top_subscription = performance_ranking[0]
        top_profit_share = (top_subscription['total_profit'] / totals['total_profit']) * 100
        
        if top_profit_share > 60:
            insights.append({
                'type': 'warning',
                'message': f"🎯 High concentration risk: {top_subscription['subscription_type']} generates {top_profit_share:.1f}% of total profit."
            })
        elif top_profit_share > 40:
            insights.append({
                'type': 'info',
                'message': f"📊 {top_subscription['subscription_type']} is your profit leader at {top_profit_share:.1f}% of total profit."
            })
    
    # Revenue per customer insights
    if totals['revenue_per_customer'] > 5000:
        insights.append({
            'type': 'success',
            'message': f"💎 High customer value with {totals['revenue_per_customer']:,.0f} AED average revenue per customer."
        })
    
    # Additional services insight
    service_revenue = sum(data['revenue'] for data in results['additional_services'].values())
    service_percentage = (service_revenue / totals['total_revenue']) * 100 if totals['total_revenue'] > 0 else 0
    
    if service_percentage < 10:
        insights.append({
            'type': 'info',
            'message': f"📈 Additional services represent only {service_percentage:.1f}% of revenue - potential growth opportunity."
        })
    elif service_percentage > 25:
        insights.append({
            'type': 'success',
            'message': f"🚀 Strong additional services generating {service_percentage:.1f}% of total revenue."
        })
    
    return insights

def generate_recommendations(results, performance_ranking):
    """Generate strategic recommendations"""
    recommendations = []
    
    totals = results['totals']
    
    # Pricing optimization recommendation
    if totals['profit_margin'] < 30:
        recommendations.append({
            'title': 'Pricing Optimization',
            'priority': 'High',
            'impact': 'High',
            'description': 'Current profit margins suggest opportunities for pricing adjustments to improve profitability.',
            'actions': [
                'Analyze competitor pricing for similar services',
                'Test price increases on low-margin subscription types',
                'Consider value-added bundles to justify premium pricing',
                'Implement dynamic pricing based on demand'
            ]
        })
    
    # Customer concentration recommendation
    if performance_ranking and len(performance_ranking) > 1:
        top_two_profit = sum(item['total_profit'] for item in performance_ranking[:2])
        concentration_ratio = (top_two_profit / totals['total_profit']) * 100
        
        if concentration_ratio > 70:
            recommendations.append({
                'title': 'Diversification Strategy',
                'priority': 'Medium',
                'impact': 'Medium',
                'description': 'High revenue concentration in top subscription types creates business risk.',
                'actions': [
                    'Develop marketing campaigns for underperforming subscription types',
                    'Create incentives to balance customer distribution',
                    'Investigate barriers to adoption for lower-performing tiers',
                    'Consider new subscription options to broaden appeal'
                ]
            })
    
    # Additional services growth
    service_revenue = sum(data['revenue'] for data in results['additional_services'].values())
    service_percentage = (service_revenue / totals['total_revenue']) * 100 if totals['total_revenue'] > 0 else 0
    
    if service_percentage < 15:
        recommendations.append({
            'title': 'Additional Services Expansion',
            'priority': 'Medium',
            'impact': 'High',
            'description': 'Additional services represent untapped revenue potential beyond core subscriptions.',
            'actions': [
                'Survey customers about desired additional services',
                'Expand marketing of existing additional services',
                'Bundle services with subscription packages',
                'Develop new high-margin service offerings'
            ]
        })
    
    # Customer acquisition recommendation
    if totals['total_customers'] < 1000:
        recommendations.append({
            'title': 'Customer Acquisition Acceleration',
            'priority': 'High',
            'impact': 'High',
            'description': 'Scale customer base to achieve economies of scale and market leadership.',
            'actions': [
                'Increase digital marketing investment',
                'Implement referral programs for existing customers',
                'Expand into new geographic markets',
                'Partner with complementary businesses for customer acquisition'
            ]
        })
    
    return recommendations[:4]  # Limit to top 4 recommendations

    