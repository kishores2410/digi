"""
24DIGI Application Configuration
Contains all default settings and constants
"""

class AppConfig:
    """Application configuration constants"""
    
    # Company Information
    COMPANY_NAME = "24DIGI"
    APP_TITLE = "24DIGI Revenue Analytics Platform"
    VERSION = "1.0.0"
    
    # Default Pricing Data
    DEFAULT_PRICING = {
        'VIP': {
            'mealsPerMonth': {'cost': 1000, 'selling': 1500, 'profit': 500},
            'meals3Months': {'cost': 3000, 'selling': 4500, 'profit': 1500},
            'deliveryPerMonth': {'cost': 200, 'selling': 200, 'profit': 0},
            'delivery3Months': {'cost': 600, 'selling': 600, 'profit': 0},
            'bracelet': {'cost': 315, 'selling': 800, 'profit': 485},
            'pointsX10': {'cost': 300, 'selling': 250, 'profit': -50},
            'digitalProfit': 500,
            'carOneMonth': {'cost': 5512.5, 'selling': 5512.5, 'profit': 0},
            'carThreeMonths': {'cost': 16537.5, 'selling': 16537.5, 'profit': 0}
        },
        'Normal': {
            'mealsPerMonth': {'cost': 900, 'selling': 1306.67, 'profit': 406.67},
            'meals3Months': {'cost': 2700, 'selling': 3920, 'profit': 1220},
            'deliveryPerMonth': {'cost': 200, 'selling': 200, 'profit': 0},
            'delivery3Months': {'cost': 600, 'selling': 600, 'profit': 0},
            'bracelet': {'cost': 315, 'selling': 600, 'profit': 285},
            'pointsX10': {'cost': 50, 'selling': 30, 'profit': -20},
            'digitalProfit': 500,
            'carOneMonth': {'cost': 6500, 'selling': 6500, 'profit': 0},
            'carThreeMonths': {'cost': 19500, 'selling': 19500, 'profit': 0}
        },
        'Custom': {
            'mealsPerMonth': {'cost': 1000, 'selling': 1500, 'profit': 500},
            'meals3Months': {'cost': 3000, 'selling': 4500, 'profit': 1500},
            'deliveryPerMonth': {'cost': 200, 'selling': 200, 'profit': 0},
            'delivery3Months': {'cost': 600, 'selling': 600, 'profit': 0},
            'braceletVIP': {'cost': 315, 'selling': 800, 'profit': 485},
            'braceletNormal': {'cost': 315, 'selling': 600, 'profit': 285},
            'pointsX10': {'cost': 0, 'selling': 0, 'profit': 0},
            'cbyiOneMonth': {'cost': 1700, 'selling': 1700, 'profit': 0},
            'cbyiThreeMonths': {'cost': 5100, 'selling': 5100, 'profit': 0},
            'cbyiBraceletVIP': {'cost': 0, 'selling': 800, 'profit': 800},
            'cbyiBraceletNormal': {'cost': 0, 'selling': 600, 'profit': 600}
        }
    }
    
    # Subscription Types and Durations
    SUBSCRIPTION_TYPES = ['VIP', 'Normal', 'Custom']
    SUBSCRIPTION_DURATIONS = [1, 3]  # months
    
    # Service Categories
    SERVICE_CATEGORIES = [
        'Subscription Packages',
        'Additional Services',
        'Events & Challenges', 
        'Car Rental',
        'CBYI Services',
        'Bracelets'
    ]
    
    # Forecasting Parameters
    FORECAST_PERIODS = [3, 6, 9, 12]  # months
    GROWTH_SCENARIOS = {
        'Conservative': {'growth_rate': 0.05, 'retention_rate': 0.85},
        'Moderate': {'growth_rate': 0.15, 'retention_rate': 0.90},
        'Aggressive': {'growth_rate': 0.30, 'retention_rate': 0.95},
        'Optimistic': {'growth_rate': 0.50, 'retention_rate': 0.98}
    }
    
    # Default Input Values
    DEFAULT_INPUTS = {
        'VIP_1_month': {'customers': 30, 'renewals': 10},
        'VIP_3_months': {'customers': 20, 'renewals': 5},
        'Normal_1_month': {'customers': 60, 'renewals': 40},
        'Normal_3_months': {'customers': 90, 'renewals': 80},
        'Custom_1_month': {'customers': 30, 'renewals': 25},
        'Custom_3_months': {'customers': 50, 'renewals': 40},
        
        # Additional Services
        'additional_bracelets': 2,
        'challenge_participants': 5,
        'adventure_participants': 5,
        'competition_participants': 5,
        'cbyi_non_subscribers': 2,
        'bracelets_non_subscribers': 2,
        'car_rental_customers': 0,
        
        # Event Fees
        'challenge_fee': 25.0,
        'adventure_fee': 40.0,
        'competition_fee': 35.0
    }
    
    # Colors for charts and UI
    COLORS = {
        'primary': '#1e3c72',
        'secondary': '#2a5298',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8'
    }
    
    # Chart Configuration
    CHART_CONFIG = {
        'color_palette': ['#1e3c72', '#2a5298', '#3d5aa8', '#5068b8', '#6377c8'],
        'background_color': '#ffffff',
        'grid_color': '#f0f0f0'
    }
