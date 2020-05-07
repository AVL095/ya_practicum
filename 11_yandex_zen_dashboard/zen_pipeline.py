# !/usr/bin/python
# -*- coding: utf-8 -*-

# импорт необходимых библиотек
import sys
import getopt
from datetime import datetime
import pandas as pd 
from sqlalchemy import create_engine
# создаем точку входа в программу 
if __name__=="__main__":
    # входные параметры пайплайна
    unixOptions = "s:e"
    gnuOptions = ["start_dt=", "end_dt="]

    fullCmdArguments = sys.argv
    argumentList = fullCmdArguments[1:]
    
    try:
        arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)   

    start_dt = ''
    end_dt = '' 
    # считывание входных параметров для start_dt, end_dt в цикле
    for currentArgument, currentValue in arguments:
        if currentArgument in ('-s', '--start_dt'):
            start_dt = currentValue
        elif currentArgument in ('-e', '--end_dt'):
            end_dt = currentValue
    # задаем параметры подключения к базе данных (БД)
    db_config = {'user':'****',
                 'pwd': '****',
                 'host':'****',
                 'port': ****,
                 'db':'****'}   
    # задаем строку подключения к БД 
    connection_string = 'postgres://{}:{}@{}:{}/{}'.format(db_config['user'],
                                                           db_config['pwd'],
                                                           db_config['host'],
                                                           db_config['port'],
                                                           db_config['db'])
    engine = create_engine(connection_string)
    # создаем SQL-запрос для чтения сырых данных


    query = ''' SELECT event_id, age_segment, event, item_id, item_topic, item_type, source_id, source_topic, source_type,
                TO_TIMESTAMP(ts / 1000) AT TIME ZONE 'Etc/UTC' as dt, user_id
                FROM log_raw
                WHERE TO_TIMESTAMP(ts / 1000) AT TIME ZONE 'Etc/UTC' BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
            '''.format(start_dt, end_dt)
    # записываем данные в датафрейм                                                      
    log_raw = pd.io.sql.read_sql(query, con=engine)
    # округляем до минут
    log_raw['dt'] = pd.to_datetime(log_raw['dt']).dt.round('min')
    # создаем агрегирующие таблицы
    dash_engagement = (log_raw
                            .groupby(['dt','item_topic', 'event', 'age_segment'])
                            .agg({'user_id':'nunique'})
                            .reset_index()
                      )

    dash_visits = (log_raw
                        .groupby(['item_topic', 'source_topic', 'age_segment', 'dt'])
                        .agg({'user_id':'count'})
                        .reset_index()
                  )

    dash_engagement = dash_engagement.rename(columns = {'user_id': 'unique_users'})
    dash_visits = dash_visits.rename(columns = {'user_id': 'visits'})
    
    # удаление ранее записанных данных
    dash_engagement = dash_engagement.fillna(0)
    dash_visits = dash_visits.fillna(0)

    tables = {'dash_engagement':dash_engagement,
              'dash_visits':dash_visits}

    for table_name, table_data in tables.items():
        query = '''
                DELETE FROM {} WHERE dt BETWEEN '{}'::TIMESTAMP 
                AND '{}'::TIMESTAMP
                '''.format(table_name, start_dt, end_dt)
        engine.execute(query)

        table_data.to_sql(name=table_name, con=engine, if_exists='append', index=False)
    print('Success!')