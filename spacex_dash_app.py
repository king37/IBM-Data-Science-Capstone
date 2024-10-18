# Import required libraries
import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get the maximum and minimum payload values
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = Dash(__name__)

# Generate options for the dropdown menu
launch_sites = spacex_df['Launch Site'].unique()
options = [{'label': 'All Sites', 'value': 'ALL'}]
options += [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    html.Div([
        dcc.Dropdown(
            id='site-dropdown',
            options=options,
            value='ALL',
            placeholder='Select a Launch Site here',
            searchable=True
        )
    ], style={'width': '80%', 'margin': 'auto'}),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    html.Div([
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={i: f'{i}' for i in range(0, 10001, 2500)},
            value=[min_payload, max_payload]
        )
    ], style={'width': '80%', 'margin': 'auto'}),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Compute the total successful launches for all sites
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Counts']
        fig = px.pie(
            success_counts,
            names='Launch Site',
            values='Counts',
            title='Total Successful Launches by Site'
        )
    else:
        # Compute success vs failure counts for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['Outcome', 'Counts']
        success_counts['Outcome'] = success_counts['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            success_counts,
            names='Outcome',
            values='Counts',
            title=f'Total Success vs Failure Launches for site {entered_site}'
        )
    return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs,
# `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')])
def update_scatter_plot(entered_site, payload_range):
    low, high = payload_range
    # Filter data based on payload range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if entered_site == 'ALL':
        # Plot for all sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for All Sites'
        )
    else:
        # Plot for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {entered_site}'
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
