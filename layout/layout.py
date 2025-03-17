from dash import dcc, html, Input, Output, State, Patch, no_update, clientside_callback, callback
from dash.dash_table import DataTable, FormatTemplate
from dash_bootstrap_templates import load_figure_template
import plotly.io as pio
import dash_bootstrap_components as dbc
import pandas as pd
from data.data import rename_for_layout
from data.db import initial_setup


import plotly.express as px
template_themes = ['vizro', 'vizro_dark']
load_figure_template(template_themes)
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.2.4/dbc.min.css"

def get_style_sheets():
    return [dbc.themes.BOOTSTRAP, dbc.themes.MINTY, dbc.icons.FONT_AWESOME, dbc_css]
# Components
children = []
def create_header():
    '''
    Dashboard Header
    '''
    return html.H1("Grocery Inventory", style={'textAlign': 'center'},id='header')
def create_color_mode_switch():
    '''
    Light and Dark mode switch
    '''
    return html.Span([dbc.Label(className="fa fa-moon", html_for="color-mode-switch"),
        dbc.Switch(id="color-mode-switch", value=False,
                   className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="color-mode-switch")])


# Load dataset (replace with your file path)
df = rename_for_layout(initial_setup())

def create_date_pickers():
    # Filters
    return html.Div([
        html.Div([html.H5('Date Received'),
            dcc.DatePickerRange(
                id='date-received',
                start_date=df['Date Received'].min(),
                end_date=df['Date Received'].max()
            )], style={'display': 'flex','margin': 'auto','flexDirection': 'column', 'alignItems': 'left'}),
            html.Div([html.H5('Last Order Date'),
            dcc.DatePickerRange(
                id='date-last-order',
                start_date=df['Last Order Date'].min(),
                end_date=df['Last Order Date'].max()
            )], style={'display': 'flex','margin': 'auto','flexDirection': 'column', 'alignItems': 'left'})
        ], style={'display': 'flex','margin': 'auto','flexDirection': 'row', 'alignItems': 'center'}
        # { 'gap': '10px',}
        )
def create_selectables():
    return html.Div([dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': cat, 'value': cat} for cat in df['Category'].unique()],
                placeholder="Select a Category",
                multi=True,
                style={'width': '35%'}
            ),
            dcc.Dropdown(
                id='product-dropdown',
                options=[{'label': cat, 'value': cat} for cat in df['Product Name'].unique()],
                placeholder="Select a Product",
                multi=True,
                style={'width': '35%'},
                searchable=True
            ),
            dcc.Checklist(df.Status.unique().tolist(),id='checklist-status'),
            ], style={'display': 'flex','margin': 'auto','flexDirection': 'row', 'alignItems': 'center'}
        )
def create_cards():
    return html.Div([
            html.Div(id='total-sales', style={'padding': '20px'
                                            #   , 'border': '1px solid black'
                                              }),
            html.Div(id='total-inventory', style={'padding': '20px'}),
            html.Div(id='avg-turn', style={'padding': '20px'})
        ],id='kpi-cards', style={'display': 'flex', 'gap': '10px', 'margin-top': '20px'})
def create_charts():
    return html.Div([
        dcc.Graph(id='sales-category'),
        dcc.Graph(id='top-products'),
        ],id='charts', style={'display': 'flex','margin': 'auto','flexDirection': 'row',})
def create_file_download_section():
    '''
    DataTable File download options and button
    '''
    file_type_header = html.H4("Choose download file type.", style={'textAlign': 'left'})
    file_type_selector = dcc.RadioItems(
        id="file-type-selector",
        options=[{"label": "Excel file", "value": "xlsx"},
                 {"label": "CSV file", "value": "csv"}],
        value='csv',
        labelStyle={'display': 'inline-block', 'margin': '10px'}
    )
    download_button = html.Button("Download Data", id='download-button', style={"marginTop": 20})
    download_component = dcc.Download(id='download')
    file_div = html.Div([file_type_header, file_type_selector], id='file-div', style={'display': 'flex', 'flex-direction': 'column', 'margin': '10px'})
    download_div = html.Div([download_button, download_component], id='download-div', style={'display': 'flex', 'flex-direction': 'column', 'margin': '10px'})
    return html.Div([file_div, download_div], id='file-download-div', style={'display': 'flex', 'flex-direction': 'row', 'margin': '10px'})
def data_table_style(dark) -> dict:
    '''
    DataTable style params for light and dark mode
    '''
    if not dark:
        return dict(style_data={
            'color': 'black',
            'backgroundColor': 'white'
        },
            style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)',
            }
        ],
            style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold'
        })

    return dict(style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white'
    },
        style_data_conditional=[],
        style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
    })
def data_table_filters(df):
    columns = ['Product Name','Category','Product Id','Supplier Name','Supplier Id','Stock Quantity','Reorder Level','Reorder Quantity','Revenue']
    return df.loc[df['Restock'] == True,columns].sort_values(by=['Revenue'],ascending=False)
def df_to_data_table(df):
    return df.to_dict(orient='records')
def create_data_table(df):
    ''''
    DataTable displaying price information for the given dates
    '''
    money = FormatTemplate.money(2)
    # percent = FormatTemplate.percentage(2, True)
    columns = ['Product Name','Category','Product Id','Supplier Name','Supplier Id','Stock Quantity','Reorder Level','Reorder Quantity','Revenue']
    dt_df = data_table_filters(df)
    print(dt_df.head())
    dt_cols = []
    for i,c in enumerate(columns):
        if i < 5:
            dt_cols.append({'name': c, 'id': c, 'type': 'text'})
        elif c == 'Revenue':
            dt_cols.append({'name': c, 'id': c, 'type': 'numeric','format':money})
        else:
            dt_cols.append({'name': c, 'id': c, 'type': 'numeric'})
    return html.Div([html.H4('Needs Replenishment'),DataTable(data=df_to_data_table(dt_df),id='data-table', page_size=10, columns=dt_cols,
                      sort_action="native", filter_action='native', style_table={"overflowX": "auto"},
    **data_table_style(False))])

def create_layout():
    return html.Div([
        create_header(),
        create_color_mode_switch(),
        create_date_pickers(),
        create_selectables(),
        create_cards(),
        create_charts(),
        create_file_download_section(),
        create_data_table(df)], className='dbc')

def filter_data(rec_start_date, rec_end_date,order_start_date, order_end_date, selected_categories,selected_products,checklist_status):
    filtered_df = pd.DataFrame
    if all([rec_start_date, rec_end_date]):
        filtered_df = df.loc[df['Date Received'].between(rec_start_date, rec_end_date),:]
    elif rec_end_date:
        filtered_df = df.loc[df['Date Received'] <= rec_end_date,:]
    if all([order_start_date, order_end_date]):
        if not filtered_df.empty:
            filtered_df = filtered_df.loc[filtered_df['Last Order Date'].between(order_start_date, order_end_date),:]
        else:
            filtered_df = df.loc[df['Last Order Date'].between(order_start_date, order_end_date),:]
    elif order_end_date:
        if not filtered_df.empty:
            filtered_df = filtered_df.loc[filtered_df['Last Order Date'] <= order_end_date,:]
        else:
            filtered_df = df.loc[df['Last Order Date'] <= order_end_date,:]
    if filtered_df.empty:
        filtered_df = df.copy()
    if selected_categories:
        filtered_df = filtered_df.loc[filtered_df['Category'].isin(selected_categories)]
    if selected_products:
        filtered_df = filtered_df.loc[filtered_df['Product Name'].isin(selected_products)]
    if checklist_status:
        filtered_df = filtered_df.loc[filtered_df['Status'].isin(checklist_status)]
    return filtered_df

def generate_kpis(filtered_df):
    total_sales = f"Total Sales: ${filtered_df['Revenue'].sum():,.0f}"
    total_orders = f"Total Inventory: ${filtered_df['Inventory Value'].sum():,.0f}"
    avg_order_value = f"Avg Turnover: {filtered_df['Inventory Turnover Rate'].mean():,.0f}"
    return total_sales, total_orders, avg_order_value

def generate_charts(filtered_df):
    cats = filtered_df.groupby('Category',as_index=False)['Revenue'].sum().sort_values(by='Revenue',ascending=False)
    top_cats = px.bar(cats,
                           x='Category', y='Revenue', title='Sales per Category',text=[f'${a:,.0f}' for a in cats['Revenue'].values.tolist()])
    top_cats.update_traces(marker_color='red')
    prods = filtered_df.groupby('Product Name')['Revenue'].sum().nlargest(10).reset_index()
    top_prods = px.bar(prods,
                           x='Product Name', y='Revenue', title='Top 10 Products',text=[f'${a:,.0f}' for a in prods['Revenue'].values.tolist()])
    # stats = filtered_df.groupby(by='Status',as_index=False)['Inventory Value'].sum()
    # inv_status = px.pie(stats, names='Status', title='Inventory Status')
    return top_cats, top_prods#, inv_status


# Initialize Dash app
# app = dash.Dash(__name__)
# app.layout = create_layout()

@callback(
    [Output('total-sales', 'children'),
     Output('total-inventory', 'children'),
     Output('avg-turn', 'children'),
     Output('sales-category', 'figure'),
     Output('top-products', 'figure'),
     Output('data-table','data')],
    [Input('date-received', 'start_date'),
     Input('date-received', 'end_date'),
     Input('date-last-order', 'start_date'),
     Input('date-last-order', 'end_date'),
     Input('category-dropdown', 'value'),
     Input('product-dropdown', 'value'),
     Input('checklist-status', 'value'),],
    #  prevent_initial_call=True,
)
def update_dashboard(rec_start_date, rec_end_date,order_start_date, order_end_date, selected_categories,selected_products,checklist_status):
    filtered_df = filter_data(rec_start_date, rec_end_date,order_start_date, order_end_date, selected_categories,selected_products,checklist_status)
    total_sales, total_inv, avg_inv_value = generate_kpis(filtered_df)
    sales_cat, top_products = generate_charts(filtered_df)
    dt_data = df_to_data_table(data_table_filters(filtered_df))
    return total_sales, total_inv, avg_inv_value, sales_cat, top_products,dt_data
    # kpis = generate_kpis(filtered_df)
    # charts = generate_charts(filtered_df)
    # results = list(kpis)
    # results.extend(list(charts))
    # return *tuple(results)#*kpis,*charts
    


@callback(
    Output('download', "data"),
    Input('download-button', "n_clicks"),
    State("file-type-selector", 'value'),
    State('data-table', "derived_virtual_data"),
    prevent_initial_call=True,
    # prevent_initial_callbacks=True,
)
def download_data(click, download_type, data):
    '''
    Download data as CSV or XLSX from DataTable
    '''
    if not click:
        return no_update
    # stock = stock_selected if not input_value else input_value
    dff = pd.DataFrame(data)
    dff.set_index(dff.columns[0], inplace=True)
    if download_type == "csv":
        writer = dff.to_csv
    else:
        writer = dff.to_excel
    return dcc.send_data_frame(writer, f"Replenishment Needs.{download_type}")


def get_template(switch_on):
    '''
    Get light or dark template
    '''
    return pio.templates[template_themes[0]] if switch_on else pio.templates[template_themes[1]]


@callback(
    # Output("stock-price-chart", "figure", allow_duplicate=True),
    Output('sales-category', 'figure', allow_duplicate=True),
     Output('top-products', 'figure', allow_duplicate=True),
    #  Output('inv-status', 'figure', allow_duplicate=True),
    Output('data-table', 'style_header'),
    Output('data-table', 'style_data_conditional'),
    Output('data-table', 'style_data'),
    Input("color-mode-switch", "value"),
    prevent_initial_call=True
)
def update_theme(switch_on):
    '''
    Update theme to light or dark
    '''
    # switch_on = Light
    # When using Patch() to update the figure template, you must use the figure template dict
    # from plotly.io  and not just the template name
    # template_themes list is ordered light to dark
    # pio.templates[template_themes[0]] if switch_on else pio.templates[template_themes[1]]
    template = get_template(switch_on)
    patches = []
    for _ in range(2):
        patched_figure = Patch()
        patched_figure["layout"]["template"] = template
        patches.append(patched_figure)
    styles = data_table_style(not (switch_on))
    patches.extend([styles['style_header'], styles['style_data_conditional'], styles['style_data']])
    return tuple(patches)
# patched_figure,patched_figure,deepcopy(patched_figure)
    # styles['style_header'], styles['style_data_conditional'], styles['style_data']


clientside_callback(
    """
    (switchOn) => {
       document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');
       return window.dash_clientside.no_update
    }
    """,
    Output("color-mode-switch", "id"),
    Input("color-mode-switch", "value"),
)

