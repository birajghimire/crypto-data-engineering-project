import os
import math
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, date
import csv
import yaml
import json


def get_data_from_api(url, headers):
    # Create api request & receive response
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result:
            data = result['data']
            return data
    else:
        print(response.status_code)


def save_json(output, path):
    if not os.path.exists(path):
        os.makedirs(path)
    
    coin_slug = output['slug']
    full_path = path + f'{coin_slug}.json'

    with open(full_path, 'w') as json_file:
        json.dump(output, json_file, indent=4)

def get_coin_id(date, path):
    path += f'{date}.csv'
    id_list = pd.read_csv(path, usecols=[0]).iloc[:, 0].tolist()
    return id_list


if __name__ == '__main__':

    # get config
    with open("config.yml", 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    url = config['API']['EXCHANGE']['INFO']
    date = config['DATE']
    raw_zone_path = config['PATH']['RAW_ZONE']
    table_name = os.path.splitext(os.path.basename(__file__))[0].split('s2r_')[-1]
    table_path = raw_zone_path + f'/{table_name}/'

    # date processing
    current_day = datetime.strptime(date, '%Y%m%d')
    previous_day = current_day - timedelta(days=1)
    time_start = previous_day.strftime('%Y-%m-%dT23:55:00Z')
    time_end = current_day.strftime('%Y-%m-%dT23:59:59Z')
    
    # api config
    API_KEY = os.environ.get('API_KEY')
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY
    }

    # get coin id
    exchange_map_path = config['PATH']['RAW_ZONE'] + '/exchange_map/'
    coin_id_list = get_coin_id(date, exchange_map_path)
    
    for coin_id in coin_id_list:
        exchange_info = get_data_from_api(url=url + f'?id={str(coin_id)}', headers=headers)
        exchange_info = exchange_info[str(coin_id)]
        save_json(output=exchange_info, path=table_path)
        


