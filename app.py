import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s==%(funcName)s==%(message)s')

pop_growth_df = pd.read_csv('data/country_data_master.csv', 
                            usecols=['country', 'lon', 'lat', 'birth_rate', 
                                     'death_rate', 'pop_growth', 'map_ref'])

map_ref = ['Africa', 'Arctic Region', 'Asia', 'Central America and the Caribbean',
           'Europe', 'Middle East', 'North America', 'South America', 'Southeast Asia']


app = dash.Dash()
server = app.server
app.title = 'Population Birth Rate, Death Rate, and Net Growth - 2017'

app.layout = html.Div([
    dcc.Graph(id='pop_barchart',
              config={'displayModeBar': False},
),
    html.Div([
        html.Div([
            dcc.Dropdown(id='countries',
                         value=tuple(),
                         placeholder='Countries',
                         multi=True,
                         options=[{'label': c, 'value': c}
                                   for c in pop_growth_df['country'].unique()]),    
        ], style={'width': '35%', 'display': 'inline-block', 'background-color': '#eeeeee'}),
        
        html.Div([
            dcc.Dropdown(id='regions',
                         value='',
                         placeholder='Regions',
                         options=[{'label': region, 'value': region}
                                  for region in map_ref]),
        ], style={'width': '35%', 'display': 'inline-block'})
    ], style={'margin-left': '25%', 'background-color': '#eeeeee'}),
    
    dcc.Graph(id='pop_growth_map',
              config={'displayModeBar': False},
              figure={'data': [go.Scattergeo(lon=pop_growth_df['lon'],
                                             lat=pop_growth_df['lat'],
                                             mode='markers',
                                             hoverinfo='text',
                                             text=pop_growth_df['country'].astype(str) + '<br>' + 'Net Population Growth: ' +
                                                  pop_growth_df['pop_growth'].div(10).round(2).astype(str) + '%',
                                             marker={'size': 22,
                                                     'color': pop_growth_df['pop_growth'].div(10),
                                                     'line': {'color': '#000000', 'width': .1},
                                                     'colorscale': [[0, 'rgba(214, 39, 40, 0.85)'], 
                                                                    [0.142, 'rgba(255, 255, 255, 0.85)'],  
                                                                    [1, 'rgba(6,54,21, 0.85)']],
                                                     'colorbar':{'outlinewidth': 0, 'ticksuffix': '%', 'tickformat': '.1f'},
                                                     'showscale': True,
                                                     },
                                             )],

                     'layout': go.Layout(title='Net Population Growth Rates per Country - 2017 (CIA World Factbook)',
                                         font={'family': 'Palatino'},
                                         titlefont={'size': 22},
                                         paper_bgcolor='#eeeeee',
                                         width=1420,
                                         height=750,
                                         geo={'showland': True, 'landcolor': '#eeeeee',
                                              'countrycolor': '#cccccc', 
                                              'showcountries': True,
                                              'oceancolor': '#eeeeee',
                                              'showocean': True,
                                              'showcoastlines': True, 
                                              'showframe': False,
                                              'coastlinecolor': '#cccccc',
                                              },
                                            )}),
    html.A('@eliasdabbas', href='https://www.twitter.com/eliasdabbas'), 
    html.P(),
    html.Content('Data: CIA World Factobook  '),
    html.A('Population Growth Rate', href='https://www.cia.gov/library/publications/the-world-factbook/fields/2002.html'),
    html.Br(),
    html.Content('  Code: '),
    html.A('github.com/eliasdabbas/population_growth', href='https://github.com/eliasdabbas/population_growth'), html.Br(), html.Br(),
    html.Content('The average annual percent change in the population, resulting from a surplus (or deficit) of births '
                 'over deaths and the balance of migrants entering and leaving a country. The rate may be positive or negative. '
                 'The growth rate is a factor in determining how great a burden would be imposed on a country by the changing '
                 'needs of its people for infrastructure (e.g., schools, hospitals, housing, roads), resources (e.g., food, '
                 'water, electricity), and jobs. Rapid population growth can be seen as threatening by neighboring countries.')
    
], style={'background-color': '#eeeeee'})

@app.callback(Output('pop_barchart', 'figure'),
             [Input('regions', 'value'), Input('countries', 'value')])
def plot_countries(region, countries):
    logging.info(msg=locals())
    df = pop_growth_df.sort_values(['pop_growth'])
    return {'data': [go.Bar(x=df['country'],
                            y=df['birth_rate'],
                            orientation='v',
                            hoverlabel={'namelength': -1, 'bgcolor': '#444444'},
                            marker={'color': '#bbbbbb'},
                            showlegend=False,
                            name='Births per 1,000'),
 
                     go.Bar(x=df[df['map_ref'] == region]['country'],
                            y=df[df['map_ref'] == region]['birth_rate'],
                            base=0,  
                            marker={'color': '#1f77b4'},
                            name=region,
                            width=0.8),
                     go.Bar(y=-df['death_rate'],
                            x=df['country'],
                            orientation='v',
                            hoverlabel={'namelength': -1, 'bgcolor': '#444444'},
                            marker={'color': '#bbbbbb'},
                            showlegend=False,
                            name='Deaths per 1,000'),
                      
                     go.Bar(x=df[df['map_ref'] == region]['country'],
                            y=-df[df['map_ref'] == region]['death_rate'],
                            base=0,
                            marker={'color': '#1f77b4'},
                            name='',
                            showlegend=False,
                            width=0.8),
                     go.Scatter(y=df['pop_growth'],
                                x=df['country'],
                                mode='markers',
                                marker={'color': 'red', 'size': 5},
                                hoverlabel={'namelength': -1},
                                showlegend=False,
                                name='Net Population Growth' )] +
                    
                    [go.Bar(x=df[df['country'] == c]['country'],
                            y=df[df['country'] == c]['birth_rate'] + df[df['country'] == c]['death_rate'],
                            base=-df[df['country'] == c]['death_rate'],
                            name=c,
                            width=0.8)
                     for c in countries],

            'layout': go.Layout(barmode='relative',
                                title='Net Population Growth per 1,000 Inhabitants - 2017 (CIA World Factbook)',
                                titlefont={'size': 22},
                                paper_bgcolor='#eeeeee',
                                plot_bgcolor='#eeeeee', 
                                margin={'r': 0, 'l': 20, 'b': 50, 't': 50},
                                height=600,
                                font={'family': 'Palatino'},
                                xaxis={'showticklabels': False, 'showgrid': True, 'nticks': int(len(df)*.1)},
                                legend={'orientation': 'h', 'x': 0.2},
                                annotations=[{'x': -8, 'y': 5 ,'text': 'Births', 'showarrow': False,
                                              'font': {'size': 17}},
                                             {'x': -8, 'y': -5 ,'text': 'Deaths', 'showarrow': False,
                                              'font': {'size': 17}}])

          }

if __name__ == '__main__':
    app.run_server()