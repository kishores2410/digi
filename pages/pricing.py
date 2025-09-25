"""
24DIGI Pricing Configuration Page
Professional pricing management interface
"""

import streamlit as st
import pandas as pd
import json
from modules.data_manager import DataManager

def render(data_manager: DataManager):
    """Render the pricing configuration page"""
    
    st.header("💰 Pricing Configuration")
    st.markdown("*Professional pricing management for all subscription tiers*")
    
    # Pricing overview
    render_pricing_overview(data_manager)
    
    # Detailed configuration
    render_detailed_pricing_config(data_manager)
    
    # Import/Export functionality
    render_import_export_section(data_manager)

def render_pricing_overview(data_manager: DataManager):
    """Render pricing overview and quick stats"""
    
    st.subheader("📊 Pricing Overview")
    
    # Create pricing summary
    pricing_summary = []
    for sub_type in ['VIP', 'Normal', 'Custom']:
        pricing = data_manager.get_pricing_data(sub_type)
        
        # Calculate package values
        package_1m = data_manager.calculate_package_cost(sub_type, 1)
        package_3m = data_manager.calculate_package_cost(sub_type, 3)
        
        pricing_summary.append({
            'Subscription Type': sub_type,
            '1-Month Package': f"{package_1m['cost']:,.0f} → {package_1m['revenue']:,.0f} AED",
            '3-Month Package': f"{package_3m['cost']:,.0f} → {package_3m['revenue']:,.0f} AED",
            '1-Month Margin': f"{(package_1m['profit']/package_1m['revenue']*100) if package_1m['revenue'] > 0 else 0:.1f}%",
            '3-Month Margin': f"{(package_3m['profit']/package_3m['revenue']*100) if package_3m['revenue'] > 0 else 0:.1f}%"
        })
    
    df_summary = pd.DataFrame(pricing_summary)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Increase All by 10%", type="secondary"):
            apply_percentage_change(data_manager, 1.10)
            st.success("✅ All prices increased by 10%")
            st.rerun()
    
    with col2:
        if st.button("📉 Decrease All by 5%", type="secondary"):
            apply_percentage_change(data_manager, 0.95)
            st.success("✅ All prices decreased by 5%")
            st.rerun()
    
    with col3:
        if st.button("🔄 Reset to Defaults", type="secondary"):
            data_manager.reset_pricing_to_defaults()
            st.success("✅ Pricing reset to defaults")
            st.rerun()

def render_detailed_pricing_config(data_manager: DataManager):
    """Render detailed pricing configuration interface"""
    
    st.subheader("⚙️ Detailed Configuration")
    
    # Select subscription type to edit
    selected_type = st.selectbox(
        "Select Subscription Type to Configure",
        ['VIP', 'Normal', 'Custom'],
        key="selected_pricing_type"
    )
    
    st.markdown(f"#### Configuring {selected_type} Pricing")
    
    pricing_data = data_manager.get_pricing_data(selected_type)
    
    # Create tabs for different service categories
    tabs = st.tabs(["🍽️ Meals & Delivery", "📿 Bracelets", "🎯 Points & Digital", "🚗 Additional Services"])
    
    with tabs[0]:
        render_meals_pricing_config(data_manager, selected_type, pricing_data)
    
    with tabs[1]:
        render_bracelet_pricing_config(data_manager, selected_type, pricing_data)
    
    with tabs[2]:
        render_points_digital_config(data_manager, selected_type, pricing_data)
    
    with tabs[3]:
        render_additional_services_config(data_manager, selected_type, pricing_data)

def render_meals_pricing_config(data_manager: DataManager, sub_type: str, pricing_data: dict):
    """Render meals and delivery pricing configuration"""
    
    st.markdown("**🍽️ Meals Pricing**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("*1 Month Package*")
        
        meal_1m_cost = st.number_input(
            "Meals 1M - Cost (AED)",
            min_value=0.0,
            value=float(pricing_data.get('mealsPerMonth', {}).get('cost', 0)),
            step=1.0,
            key=f"{sub_type}_meal_1m_cost"
        )
        
        meal_1m_selling = st.number_input(
            "Meals 1M - Selling (AED)",
            min_value=0.0,
            value=float(pricing_data.get('mealsPerMonth', {}).get('selling', 0)),
            step=1.0,
            key=f"{sub_type}_meal_1m_selling"
        )
        
        st.info(f"Profit: {meal_1m_selling - meal_1m_cost:,.0f} AED ({((meal_1m_selling - meal_1m_cost)/meal_1m_selling*100) if meal_1m_selling > 0 else 0:.1f}%)")
    
    with col2:
        st.markdown("*3 Month Package*")
        
        meal_3m_cost = st.number_input(
            "Meals 3M - Cost (AED)",
            min_value=0.0,
            value=float(pricing_data.get('meals3Months', {}).get('cost', 0)),
            step=1.0,
            key=f"{sub_type}_meal_3m_cost"
        )
        
        meal_3m_selling = st.number_input(
            "Meals 3M - Selling (AED)",
            min_value=0.0,
            value=float(pricing_data.get('meals3Months', {}).get('selling', 0)),
            step=1.0,
            key=f"{sub_type}_meal_3m_selling"
        )
        
        st.info(f"Profit: {meal_3m_selling - meal_3m_cost:,.0f} AED ({((meal_3m_selling - meal_3m_cost)/meal_3m_selling*100) if meal_3m_selling > 0 else 0:.1f}%)")
    
    st.markdown("**🚚 Delivery Pricing**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        delivery_1m_cost = st.number_input(
            "Delivery 1M - Cost (AED)",
            min_value=0.0,
            value=float(pricing_data.get('deliveryPerMonth', {}).get('cost', 0)),
            step=1.0,
            key=f"{sub_type}_delivery_1m_cost"
        )
        
        delivery_1m_selling = st.number_input(
            "Delivery 1M - Selling (AED)",
            min_value=0.0,
            value=float(pricing_data.get('deliveryPerMonth', {}).get('selling', 0)),
            step=1.0,
            key=f"{sub_type}_delivery_1m_selling"
        )
    
    with col2:
        delivery_3m_cost = st.number_input(
            "Delivery 3M - Cost (AED)",
            min_value=0.0,
            value=float(pricing_data.get('delivery3Months', {}).get('cost', 0)),
            step=1.0,
            key=f"{sub_type}_delivery_3m_cost"
        )
        
        delivery_3m_selling = st.number_input(
            "Delivery 3M - Selling (AED)",
            min_value=0.0,
            value=float(pricing_data.get('delivery3Months', {}).get('selling', 0)),
            step=1.0,
            key=f"{sub_type}_delivery_3m_selling"
        )
    
    # Update pricing data
    if st.button(f"💾 Update {sub_type} Meals & Delivery", key=f"update_{sub_type}_meals"):
        updates = {
            'mealsPerMonth': {'cost': meal_1m_cost, 'selling': meal_1m_selling, 'profit': meal_1m_selling - meal_1m_cost},
            'meals3Months': {'cost': meal_3m_cost, 'selling': meal_3m_selling, 'profit': meal_3m_selling - meal_3m_cost},
            'deliveryPerMonth': {'cost': delivery_1m_cost, 'selling': delivery_1m_selling, 'profit': delivery_1m_selling - delivery_1m_cost},
            'delivery3Months': {'cost': delivery_3m_cost, 'selling': delivery_3m_selling, 'profit': delivery_3m_selling - delivery_3m_cost}
        }
        data_manager.update_pricing_data(sub_type, updates)
        st.success("✅ Meals & Delivery pricing updated!")

def render_bracelet_pricing_config(data_manager: DataManager, sub_type: str, pricing_data: dict):
    """Render bracelet pricing configuration"""
    
    st.markdown("**📿 Bracelet Pricing**")
    
    if sub_type == 'Custom':
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("*VIP Bracelet*")
            bracelet_vip_cost = st.number_input(
                "VIP Bracelet - Cost (AED)",
                min_value=0.0,
                value=float(pricing_data.get('braceletVIP', {}).get('cost', 0)),
                step=1.0,
                key=f"{sub_type}_bracelet_vip_cost"
            )
            
            bracelet_vip_selling = st.number_input(
                "VIP Bracelet - Selling (AED)",
                min_value=0.0,
                value=float(pricing_data.get('braceletVIP', {}).get('selling', 0)),
                step=1.0,
                key=f"{sub_type}_bracelet_vip_selling"
            )
        
        with col2:
            st.markdown("*Normal Bracelet*")
            bracelet_normal_cost = st.number_input(
                "Normal Bracelet - Cost (AED)",
                min_value=0.0,
                value=float(pricing_data.get('braceletNormal', {}).get('cost', 0)),
                step=1.0,
                key=f"{sub_type}_bracelet_normal_cost"
            )
            
            bracelet_normal_selling = st.number_input(
                "Normal Bracelet - Selling (AED)",
                min_value=0.0,
                value=float(pricing_data.get('braceletNormal', {}).get('selling', 0)),
                step=1.0,
                key=f"{sub_type}_bracelet_normal_selling"
            )
        
        if st.button(f"💾 Update {sub_type} Bracelets", key=f"update_{sub_type}_bracelets"):
            updates = {
                'braceletVIP': {'cost': bracelet_vip_cost, 'selling': bracelet_vip_selling, 'profit': bracelet_vip_selling - bracelet_vip_cost},
                'braceletNormal': {'cost': bracelet_normal_cost, 'selling': bracelet_normal_selling, 'profit': bracelet_normal_selling - bracelet_normal_cost}
            }
            data_manager.update_pricing_data(sub_type, updates)
            st.success("✅ Bracelet pricing updated!")
    
    else:
        bracelet_cost = st.number_input(
            "Bracelet - Cost (AED)",
            min_value=0.0,
            value=float(pricing_data.get('bracelet', {}).get('cost', 0)),
            step=1.0,
            key=f"{sub_type}_bracelet_cost"
        )
        
        bracelet_selling = st.number_input(
            "Bracelet - Selling (AED)",
            min_value=0.0,
            value=float(pricing_data.get('bracelet', {}).get('selling', 0)),
            step=1.0,
            key=f"{sub_type}_bracelet_selling"
        )
        
        st.info(f"Profit: {bracelet_selling - bracelet_cost:,.0f} AED ({((bracelet_selling - bracelet_cost)/bracelet_selling*100) if bracelet_selling > 0 else 0:.1f}%)")
        
        if st.button(f"💾 Update {sub_type} Bracelet", key=f"update_{sub_type}_bracelet"):
            updates = {
                'bracelet': {'cost': bracelet_cost, 'selling': bracelet_selling, 'profit': bracelet_selling - bracelet_cost}
            }
            data_manager.update_pricing_data(sub_type, updates)
            st.success("✅ Bracelet pricing updated!")

def render_points_digital_config(data_manager: DataManager, sub_type: str, pricing_data: dict):
    """Render points and digital services configuration"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Points X10**")
        
        points_cost = st.number_input(
            "Points X10 - Cost (AED)",
            min_value=0.0,
            value=float(pricing_data.get('pointsX10', {}).get('cost', 0)),
            step=1.0,
            key=f"{sub_type}_points_cost"
        )
        
        points_selling = st.number_input(
            "Points X10 - Selling (AED)",
            min_value=0.0,
            value=float(pricing_data.get('pointsX10', {}).get('selling', 0)),
            step=1.0,
            key=f"{sub_type}_points_selling"
        )
        
        st.info(f"Profit: {points_selling - points_cost:,.0f} AED")
    
    with col2:
        if sub_type != 'Custom':
            st.markdown("**💻 Digital Services**")
            
            digital_profit = st.number_input(
                "Digital Profit per Customer (AED)",
                min_value=0.0,
                value=float(pricing_data.get('digitalProfit', 0)),
                step=1.0,
                key=f"{sub_type}_digital_profit"
            )
            
            st.info("Pure profit - no direct costs")
    
    if st.button(f"💾 Update {sub_type} Points & Digital", key=f"update_{sub_type}_points"):
        updates = {
            'pointsX10': {'cost': points_cost, 'selling': points_selling, 'profit': points_selling - points_cost}
        }
        
        if sub_type != 'Custom':
            updates['digitalProfit'] = digital_profit
        
        data_manager.update_pricing_data(sub_type, updates)
        st.success("✅ Points & Digital pricing updated!")

def render_additional_services_config(data_manager: DataManager, sub_type: str, pricing_data: dict):
    """Render additional services configuration"""
    
    if sub_type == 'Custom':
        st.markdown("**🤖 CBYI Services**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cbyi_1m_cost = st.number_input(
                "CBYI 1M - Cost (AED)",
                min_value=0.0,
                value=float(pricing_data.get('cbyiOneMonth', {}).get('cost', 0)),
                step=1.0,
                key=f"{sub_type}_cbyi_1m_cost"
            )
            
            cbyi_1m_selling = st.number_input(
                "CBYI 1M - Selling (AED)",
                min_value=0.0,
                value=float(pricing_data.get('cbyiOneMonth', {}).get('selling', 0)),
                step=1.0,
                key=f"{sub_type}_cbyi_1m_selling"
            )
        
        with col2:
            cbyi_3m_cost = st.number_input(
                "CBYI 3M - Cost (AED)",
                min_value=0.0,
                value=float(pricing_data.get('cbyiThreeMonths', {}).get('cost', 0)),
                step=1.0,
                key=f"{sub_type}_cbyi_3m_cost"
            )
            
            cbyi_3m_selling = st.number_input(
                "CBYI 3M - Selling (AED)",
                min_value=0.0,
                value=float(pricing_data.get('cbyiThreeMonths', {}).get('selling', 0)),
                step=1.0,
                key=f"{sub_type}_cbyi_3m_selling"
            )
        
        if st.button(f"💾 Update CBYI Services", key=f"update_{sub_type}_cbyi"):
            updates = {
                'cbyiOneMonth': {'cost': cbyi_1m_cost, 'selling': cbyi_1m_selling, 'profit': cbyi_1m_selling - cbyi_1m_cost},
                'cbyiThreeMonths': {'cost': cbyi_3m_cost, 'selling': cbyi_3m_selling, 'profit': cbyi_3m_selling - cbyi_3m_cost}
            }
            data_manager.update_pricing_data(sub_type, updates)
            st.success("✅ CBYI pricing updated!")
    
    else:
        st.markdown("**🚗 Car Rental Services**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            car_1m_cost = st.number_input(
                "Car 1M - Cost (AED)",
                min_value=0.0,
                value=float(pricing_data.get('carOneMonth', {}).get('cost', 0)),
                step=1.0,
                key=f"{sub_type}_car_1m_cost"
            )
            
            car_1m_selling = st.number_input(
                "Car 1M - Selling (AED)",
                min_value=0.0,
                value=float(pricing_data.get('carOneMonth', {}).get('selling', 0)),
                step=1.0,
                key=f"{sub_type}_car_1m_selling"
            )
        
        with col2:
            car_3m_cost = st.number_input(
                "Car 3M - Cost (AED)",
                min_value=0.0,
                value=float(pricing_data.get('carThreeMonths', {}).get('cost', 0)),
                step=1.0,
                key=f"{sub_type}_car_3m_cost"
            )
            
            car_3m_selling = st.number_input(
                "Car 3M - Selling (AED)",
                min_value=0.0,
                value=float(pricing_data.get('carThreeMonths', {}).get('selling', 0)),
                step=1.0,
                key=f"{sub_type}_car_3m_selling"
            )
        
        if st.button(f"💾 Update Car Rental", key=f"update_{sub_type}_car"):
            updates = {
                'carOneMonth': {'cost': car_1m_cost, 'selling': car_1m_selling, 'profit': car_1m_selling - car_1m_cost},
                'carThreeMonths': {'cost': car_3m_cost, 'selling': car_3m_selling, 'profit': car_3m_selling - car_3m_cost}
            }
            data_manager.update_pricing_data(sub_type, updates)
            st.success("✅ Car rental pricing updated!")

def render_import_export_section(data_manager: DataManager):
    """Render import/export functionality"""
    
    st.subheader("💾 Import/Export Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📤 Export Configuration**")
        
        config_json = data_manager.export_pricing_config()
        
        st.download_button(
            label="📥 Download Pricing Config",
            data=config_json,
            file_name="24digi_pricing_config.json",
            mime="application/json",
            help="Download current pricing configuration as JSON file"
        )
        
        if st.checkbox("Show JSON Preview", key="show_json_preview"):
            st.json(json.loads(config_json))
    
    with col2:
        st.markdown("**📤 Import Configuration**")
        
        uploaded_file = st.file_uploader(
            "Choose pricing config file",
            type=['json'],
            help="Upload a previously exported pricing configuration"
        )
        
        if uploaded_file is not None:
            try:
                config_content = uploaded_file.read().decode('utf-8')
                
                if st.button("🔄 Import Configuration", type="primary"):
                    if data_manager.import_pricing_config(config_content):
                        st.success("✅ Pricing configuration imported successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid configuration file format")
                
                # Preview imported data
                with st.expander("Preview Import Data"):
                    try:
                        preview_data = json.loads(config_content)
                        st.json(preview_data)
                    except:
                        st.error("Invalid JSON format")
                        
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

def apply_percentage_change(data_manager: DataManager, multiplier: float):
    """Apply percentage change to all pricing"""
    for sub_type in ['VIP', 'Normal', 'Custom']:
        pricing = data_manager.get_pricing_data(sub_type)
        
        updated_pricing = {}
        for service_key, service_data in pricing.items():
            if isinstance(service_data, dict) and 'cost' in service_data:
                updated_pricing[service_key] = {
                    'cost': service_data['cost'] * multiplier,
                    'selling': service_data['selling'] * multiplier,
                    'profit': (service_data['selling'] * multiplier) - (service_data['cost'] * multiplier)
                }
            elif isinstance(service_data, (int, float)):
                updated_pricing[service_key] = service_data * multiplier
            else:
                updated_pricing[service_key] = service_data
        
        data_manager.update_pricing_data(sub_type, updated_pricing)
