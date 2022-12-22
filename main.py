import csv
import datetime
import xml.etree.ElementTree as ET
from urllib.request import urlopen
import pandas as pd


def date_by_parametr(date_list, parameter):
    result_date = date_list[0]
    for date in date_list:
        if parameter == 'max':
            if date > result_date:
                result_date = date
        else:
            if date < result_date:
                result_date = date
    return result_date


with open('data/vacancies_dif_currencies.csv', mode='r', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    time = []
    values = {'KZT': 0,
               'UAH': 0,
               'AZN': 0,
               'UZS': 0,
               'EUR': 0,
               'RUR': 0,
               'GEL': 0,
               'BYR': 0,
               'USD': 0,
               'KGS': 0
              }

    for line in reader:
        if line[5] != 'published_at':
            time.append(line[5])
        if line[3] != 'salary_currency' and line[3] != '':
            values[line[3]] += 1
    for value in values.keys():
        print(f'{value} - {values[value]}')

    def get_value(value):
        if values.get(value) is not None and values.get(value) > 5000:
            return value

    max_date = date_by_parametr(time, 'max')
    min_date = date_by_parametr(time, 'min')
    first_date = datetime.datetime.strptime(f'{min_date[8 :10]}-{min_date[5 :7]}-{min_date[0 :4]}', '%d-%m-%Y')
    second_date = datetime.datetime.strptime(f'{max_date[8 :10]}-{max_date[5 :7]}-{max_date[0 :4]}', '%d-%m-%Y')

    def month_count(first_date, second_date):
        months = 0
        while first_date < second_date:
            first_date = first_date + datetime.timedelta(days=30)
            months += 1
        return months - 1

    date = f'{min_date[8 :10]}/{min_date[5 :7]}/{min_date[0 :4]}'
    kzt_list = []
    uah_list = []
    eur_list = []
    byr_list = []
    usd_list = []
    date_list = []
    for i in range(month_count(first_date, second_date)):
        date_list.append(date)
        tree = ET.parse(urlopen(f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={date}'))
        date = str(datetime.datetime.strptime(date.replace('/','-'), '%d-%m-%Y') + datetime.timedelta(days=30))
        date = f'{date[8:10]}/{date[5:7]}/{date[0:4]}'
        root = tree.getroot()

        for child in root.findall("Valute"):
            charcode = child.find("CharCode").text
            value = float((child.find("Value").text).replace(',', '.')) / int(child.find("Nominal").text)
            if get_value(charcode) or charcode == 'BYN':
                if charcode == 'KZT':
                    kzt_list.append(value)
                if charcode == 'UAH':
                    uah_list.append(value)
                if charcode == 'EUR':
                    eur_list.append(value)
                if charcode == 'BYR' or charcode == 'BYN':
                    byr_list.append(value)
                if charcode == 'USD':
                    usd_list.append(value)


def get_result():
    dict_csv = {'date': date_list, 'KZT': kzt_list, 'UAH': uah_list,
                'EUR': eur_list, 'BYR': byr_list, 'USD': usd_list}
    dict_df = pd.DataFrame(dict_csv)
    dict_df.to_csv('data/dataframe.csv', index=False)


if __name__ == 'main':
    get_result()
