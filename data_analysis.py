# app.py
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

class SuperstoreDashboard:
    def __init__(self, data_path):
        """Initialize dashboard with Superstore data"""
        try:
            # Load data
            self.df = pd.read_csv(data_path)
            print("Columns in dataset:", self.df.columns.tolist())
            self.preprocess_data()
            self.calculate_metrics()
            self.init_app()
        except Exception as e:
            print(f"Error initializing dashboard: {str(e)}")
            raise

    def preprocess_data(self):
        """Prepare Superstore data"""
        try:
            # Convert dates using DD/MM/YYYY format
            self.df['Order Date'] = pd.to_datetime(self.df['Order Date'], format='%d/%m/%Y')
            self.df['Ship Date'] = pd.to_datetime(self.df['Ship Date'], format='%d/%m/%Y')
            
            # Create time-based features
            self.df['Year'] = self.df['Order Date'].dt.year
            self.df['Month'] = self.df['Order Date'].dt.month_name()
            self.df['Quarter'] = self.df['Order Date'].dt.quarter
            self.df['WeekDay'] = self.df['Order Date'].dt.day_name()
            
            # Calculate shipping duration
            self.df['Shipping Days'] = (self.df['Ship Date'] - self.df['Order Date']).dt.days
            
            print("Data preprocessing completed successfully!")
            
        except Exception as e:
            print(f"Error in preprocessing: {str(e)}")
            raise

    def calculate_metrics(self):
        """Calculate key business metrics"""
        self.metrics = {
            'total_sales': self.df['Sales'].sum(),
            'total_orders': len(self.df['Order ID'].unique()),
            'avg_order_value': self.df['Sales'].mean(),
            'unique_customers': len(self.df['Customer ID'].unique())
        }

    def init_app(self):
        """Initialize Dash app"""
        self.app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
        
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col(html.H1("Superstore Sales Analytics",
                               className="text-primary text-center my-4"))
            ]),
            
            # KPI Cards Row
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Sales", className="card-title text-success"),
                        html.H2(f"${self.metrics['total_sales']:,.2f}")
                    ])
                ]), width=3),
                
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Orders", className="card-title text-info"),
                        html.H2(f"{self.metrics['total_orders']:,}")
                    ])
                ]), width=3),
                
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H4("Avg Order Value", className="card-title text-warning"),
                        html.H2(f"${self.metrics['avg_order_value']:,.2f}")
                    ])
                ]), width=3),
                
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H4("Unique Customers", className="card-title text-danger"),
                        html.H2(f"{self.metrics['unique_customers']:,}")
                    ])
                ]), width=3),
            ], className="mb-4"),
            
            # Filters
            dbc.Row([
                dbc.Col([
                    html.Label("Select Category:"),
                    dcc.Dropdown(
                        id='category-filter',
                        options=[{'label': x, 'value': x} 
                                for x in self.df['Category'].unique()],
                        value=None,
                        multi=True
                    )
                ], width=4),
                
                dbc.Col([
                    html.Label("Select Region:"),
                    dcc.Dropdown(
                        id='region-filter',
                        options=[{'label': x, 'value': x} 
                                for x in self.df['Region'].unique()],
                        value=None,
                        multi=True
                    )
                ], width=4),
                
                dbc.Col([
                    html.Label("Select Year:"),
                    dcc.Dropdown(
                        id='year-filter',
                        options=[{'label': str(x), 'value': x} 
                                for x in sorted(self.df['Year'].unique())],
                        value=self.df['Year'].max()
                    )
                ], width=4)
            ], className="mb-4"),
            
            # Main Content Tabs
            dbc.Tabs([
                # Sales Analysis Tab
                dbc.Tab(label="Sales Analysis", children=[
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='monthly-sales-trend')
                        ], width=8),
                        
                        dbc.Col([
                            dcc.Graph(id='sales-by-category')
                        ], width=4)
                    ], className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='sales-by-region')
                        ], width=6),
                        
                        dbc.Col([
                            dcc.Graph(id='sales-by-segment')
                        ], width=6)
                    ])
                ]),
                
                # Customer Analysis Tab
                dbc.Tab(label="Customer Analysis", children=[
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='customer-segments')
                        ], width=6),
                        
                        dbc.Col([
                            dcc.Graph(id='customer-region-distribution')
                        ], width=6)
                    ], className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='customer-order-patterns')
                        ], width=12)
                    ])
                ]),
                
                # Product Analysis Tab
                dbc.Tab(label="Product Analysis", children=[
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='product-subcategory-sales')
                        ], width=12)
                    ], className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='top-products')
                        ], width=6),
                        
                        dbc.Col([
                            dcc.Graph(id='category-trends')
                        ], width=6)
                    ])
                ])
            ])
        ], fluid=True)
        
        self.setup_callbacks()

    def setup_callbacks(self):
        @self.app.callback(
            [Output('monthly-sales-trend', 'figure'),
             Output('sales-by-category', 'figure'),
             Output('sales-by-region', 'figure'),
             Output('sales-by-segment', 'figure'),
             Output('customer-segments', 'figure'),
             Output('customer-region-distribution', 'figure'),
             Output('customer-order-patterns', 'figure'),
             Output('product-subcategory-sales', 'figure'),
             Output('top-products', 'figure'),
             Output('category-trends', 'figure')],
            [Input('category-filter', 'value'),
             Input('region-filter', 'value'),
             Input('year-filter', 'value')]
        )
        def update_graphs(categories, regions, year):
            # Filter data based on selections
            dff = self.df.copy()
            if categories:
                dff = dff[dff['Category'].isin(categories)]
            if regions:
                dff = dff[dff['Region'].isin(regions)]
            if year:
                dff = dff[dff['Year'] == year]
            
            # Create figures
            monthly_trend = px.line(
                dff.groupby('Month')['Sales'].sum().reset_index(),
                x='Month',
                y='Sales',
                title='Monthly Sales Trend'
            )
            
            category_sales = px.pie(
                dff.groupby('Category')['Sales'].sum().reset_index(),
                values='Sales',
                names='Category',
                title='Sales by Category'
            )
            
            region_sales = px.bar(
                dff.groupby('Region')['Sales'].sum().reset_index(),
                x='Region',
                y='Sales',
                title='Sales by Region'
            )
            
            segment_sales = px.bar(
                dff.groupby('Segment')['Sales'].sum().reset_index(),
                x='Segment',
                y='Sales',
                title='Sales by Segment'
            )
            
            customer_segments = px.scatter(
                dff.groupby('Customer ID').agg({
                    'Sales': 'sum',
                    'Order ID': 'count'
                }).reset_index(),
                x='Sales',
                y='Order ID',
                title='Customer Segmentation'
            )
            
            customer_region = px.pie(
                dff.groupby('Region')['Customer ID'].nunique().reset_index(),
                values='Customer ID',
                names='Region',
                title='Customers by Region'
            )
            
            order_patterns = px.density_heatmap(
                dff,
                x='WeekDay',
                y='Month',
                z='Sales',
                title='Order Patterns'
            )
            
            subcategory_sales = px.treemap(
                dff.groupby(['Category', 'Sub-Category'])['Sales'].sum().reset_index(),
                path=[px.Constant('All'), 'Category', 'Sub-Category'],
                values='Sales',
                title='Sales by Sub-Category'
            )
            
            top_products = px.bar(
                dff.groupby('Product Name')['Sales'].sum()
                   .nlargest(10).sort_values(ascending=True).reset_index(),
                x='Sales',
                y='Product Name',
                orientation='h',
                title='Top 10 Products'
            )
            
            category_trend = px.line(
                dff.groupby(['Month', 'Category'])['Sales'].sum().reset_index(),
                x='Month',
                y='Sales',
                color='Category',
                title='Category Sales Trends'
            )
            
            return [monthly_trend, category_sales, region_sales, segment_sales,
                   customer_segments, customer_region, order_patterns,
                   subcategory_sales, top_products, category_trend]

    def run_server(self, debug=True, port=8050):
        """Run the dashboard server"""
        self.app.run_server(debug=debug, port=port)

if __name__ == '__main__':
    dashboard = SuperstoreDashboard('train.csv')
    dashboard.run_server()