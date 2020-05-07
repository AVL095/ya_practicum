#!/usr/bin/python
# -*- coding: utf-8 -*-

# импорт необходимых библиотек
# импорт библиотек dash
import dash 
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output 

# импорт plotly, pandas, numpy
import plotly.graph_objs as go 
from datetime import datetime
import numpy as np 
import pandas as pd 

# подключаемся к БД
from sqlalchemy import create_engine
# задаем параметры подключения к БД
db_config = {'user':'****',
             'pwd':'****',
             'host':'****',
             'port':****,
             'db':'****'}
# задаем строку подключения к БД
connection_string = 'postgres://{}:{}@{}:{}/{}'.format(db_config['user'],
                                                       db_config['pwd'],
                                                       db_config['host'],
                                                       db_config['port'],
                                                       db_config['db'])

engine = create_engine(connection_string)

# выбираем все данные из таблицы dash_visits
# и записываем их в соответствующий датафрейм
query = '''
            SELECT * FROM dash_visits
        '''
dash_visits = pd.io.sql.read_sql(query, con=engine)

# выбираем все данные из таблицы dash_engagement
# и записываем их в соответствующий датафрейм

query = '''
            SELECT * FROM dash_engagement
        '''
dash_engagement = pd.io.sql.read_sql(query, con=engine)

# приводим столбец dt к datetime
dash_visits['dt'] = pd.to_datetime(dash_visits['dt'], format='%Y-%m-%d %H:%M:%S')
dash_engagement['dt'] = pd.to_datetime(dash_engagement['dt'], format='%Y-%m-%d %H:%M:%S')

note = '''
        Этот дашборд показывает взаимодействие пользователей Яндекс.Дзена
        с карточками и темами статей
       '''
# создаем layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, compress=False) 
app.layout = html.Div(children=[

    # задаем заголовок 
    html.H1(children = 'Дашборд Яндекс.Дзен'),
    #html.Br(),
    # описание дашборда
    html.Label(note),
    html.Div([
        html.Div([
            # Выбор диапазона дат
            html.Div([
                html.Label('Выбор диапазона дат'),
                dcc.DatePickerRange(
                    start_date = dash_engagement['dt'].min().strftime('%Y-%m-%d'),
                    end_date = datetime(2019,9,25).strftime('%Y-%m-%d'),
                    display_format = 'YYYY-MM-DD',
                    id = 'dt_selector',
                ),
            ], className='filter'),

            # Выбор возрастного сегмента
            html.Div([
                html.Label('Выбор возрастного сегмента'),
                dcc.Dropdown(
                    options = [{'label':x, 'value':x} for x in dash_visits['age_segment'].unique()],
                    value = dash_visits['age_segment'].unique().tolist(),
                    multi = True,
                    id = 'age_segment_selector',
                )
            ], className='filter'),
        ], className='six columns'),

        html.Div([
            html.Label('Выбор тем карточек'),
            dcc.Dropdown(
                options = [{'label':x, 'value':x} for x in dash_visits['item_topic'].unique()],
                value = dash_visits['item_topic'].unique().tolist(),
                multi = True,
                id = 'item_topic_selector',
            )
        ], className='six columns'),
    ], className='row'),

    # Размечаем графики

    # график stacked area
    html.Div([
        html.Div([
            html.Label('График истории событий по темам карточек'),
            dcc.Graph(
                style={'height':'50vw'},
                id = 'history_absolute_visits'
            ),
        ], className='six columns'),
        # график pie-chart
        html.Div([
            html.Div([
                html.Label('Диаграмма событий по темам источников'),
                dcc.Graph(
                    style={'height':'25vw'},
                    id = 'pie_visits'
                )
            ], className='pie'),
            # график bar-chart с накоплением
            html.Div([
                html.Label('Диаграмма глубины взаимодействия'),
                dcc.Graph(
                    style={'height':'25vw'},
                    id = 'engagement_graph'
                )
            ], className='bar'),
        ], className='six columns'),
    ], className='row')
])        

# логика дашборда
# создаем декоратор

@app.callback(
    [Output('history_absolute_visits','figure'),
     Output('pie_visits','figure'),
     Output('engagement_graph','figure'),
    ],
    [Input('item_topic_selector', 'value'),
     Input('age_segment_selector', 'value'),
     Input('dt_selector','start_date'),
     Input('dt_selector','end_date'),
    ])


def update_figures(selected_item_topics, selected_ages, start_date, end_date):
    
    # условие фильтрации
    query_statement = 'item_topic in @selected_item_topics and \
                       dt >= @start_date and dt <= @end_date \
                       and age_segment in @selected_ages'

    # фильтруем таблицу dash_visits по условию
    filtered_dash_visits = (dash_visits
        .query(query_statement))

    # фильтруем таблицу dash_engagement по условию
    filtered_dash_engagement = (dash_engagement
        .query(query_statement))

    # проводим группировку для построения stacked area
    grouped_to_scatter_dash_visits = (filtered_dash_visits
        .groupby(['item_topic', 'dt'])
        .agg({'visits':'sum'})
        .sort_values(by='visits', ascending=False)
        .reset_index())
        
    # проводим группировку для построения pie-chart
    groped_to_pie_dash_visits = (filtered_dash_visits
        .groupby('source_topic')
        .agg({'visits':'sum'})
        .reset_index())
    # проводим группировку для построения bar-chart
    grouped_to_bar_dash_engagement = (filtered_dash_engagement
        .groupby('event')
        .agg({'unique_users':'mean'})
        .rename(columns={'unique_users':'average_unique_users'})
        .sort_values(by='average_unique_users', ascending=False)
        .reset_index())

    # График истории событий по темам карточек
    history_visits_by_item_topic = []
    for item_topic in grouped_to_scatter_dash_visits['item_topic'].unique():
        history_visits_by_item_topic += [go.Scatter(x = grouped_to_scatter_dash_visits.query('item_topic==@item_topic')['dt'],
                                      y = grouped_to_scatter_dash_visits.query('item_topic==@item_topic')['visits'],
                                      mode='lines',
                                      stackgroup='one',
                                      name=item_topic)]
    # Диаграмма событий по темам источников
    pie_by_source_topic = [go.Pie(labels = groped_to_pie_dash_visits['source_topic'],
                                  values = groped_to_pie_dash_visits['visits'])]

    # Проводим нормировку относительно среднего числа показов и выражаем результат в процентах
    grouped_to_bar_dash_engagement['average_unique_users'] = ((grouped_to_bar_dash_engagement['average_unique_users']\
         / grouped_to_bar_dash_engagement['average_unique_users'].max())*100).round(2)
    
    # Диаграмма глубины взаимодействия
    bar_for_engagement = [go.Bar(x = grouped_to_bar_dash_engagement['event'],
                                 y = grouped_to_bar_dash_engagement['average_unique_users'],
                                 )]
                                 


    return (
                # График истории событий по темам карточек
                {
                    'data':history_visits_by_item_topic,
                    'layout':go.Layout(xaxis={'title':'Дата'},
                                       yaxis={'title':'Количество просмотров карточек'})

                },
                # Диаграмма событий по темам источников
                {
                    'data':pie_by_source_topic,
                    'layout':go.Layout()
                },
                # Диаграмма глубины взаимодействия
                {
                    'data':bar_for_engagement,
                    'layout':go.Layout(xaxis={'title':'События'},
                                       yaxis={'title':'Средний % от показов (уникальные события)'})
                },

            )



# запуск дашборда на локальной машине

if __name__ == '__main__':
    app.run_server(debug=True)

# запуск дашборда на виртуальной машине
"""
if __name__ == '__main__':
    app.run_server(debug = True, host='0.0.0.0')
"""