import pandas as pd
import glob
from datetime import datetime, timedelta


# Функция для обработки столбца 'Марка'
def process_brand_column(df):
    new_rows = []  # Список для новых строк, которые мы создадим

    for _, row in df.iterrows():
        mark_value = row['Марка']

        # Если есть '-', обрезаем до первого '-'
        if '-' in mark_value:
            mark_value = mark_value.split('-')[0]

        # Если есть '/', разделяем строку на несколько строк
        if '/' in mark_value:
            marks = mark_value.split('/')
            for mark in marks:
                new_row = row.copy()
                new_row['Марка'] = mark.strip()  # Присваиваем новый "Марка"
                new_rows.append(new_row)
        else:
            row['Марка'] = mark_value
            new_rows.append(row)

    return pd.DataFrame(new_rows)


def expand_date_range(start_date, end_date):
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.date())
        current_date += timedelta(days=1)
    return dates


# 1. Загрузка и обработка данных о пожарах
fires_df = pd.read_csv('data/fires.csv')
fires_df['Дата начала'] = pd.to_datetime(fires_df['Дата начала'])
fires_df['Дата оконч.'] = pd.to_datetime(fires_df['Дата оконч.'])
fires_df['Марка'] = fires_df['Груз']

# Вычисление длительности пожара в часах
fires_df['Длительность'] = (fires_df['Дата оконч.'] - fires_df['Дата начала']).dt.total_seconds() / 3600

# Создаем полный список дней с пожарами
fire_days_all = []
for _, row in fires_df.iterrows():
    days = expand_date_range(row['Дата начала'], row['Дата оконч.'])
    for day in days:
        fire_days_all.append({
            'Дата акта': datetime.combine(day, datetime.min.time()),
            'Склад': row['Склад'],
            'Штабель': row['Штабель'],
            'fire': 1,
            'Вес': row['Вес по акту, тн'],  # Добавляем столбец "Вес"
            'Длительность': row['Длительность'],  # Добавляем столбец "Длительность" в часах
            'Марка': row['Марка']  # Добавляем столбец "Марка"
        })

fires_daily = pd.DataFrame(fire_days_all).drop_duplicates()

# 2. Загрузка и обработка temperature.csv
temp_df = pd.read_csv('data/temperature.csv')
temp_df['Дата акта'] = pd.to_datetime(temp_df['Дата акта'])

temp_df = process_brand_column(temp_df)

# 3. Объединение данных о пожарах с temperature.csv
temp_df['merge_key'] = temp_df['Дата акта'].dt.strftime('%Y-%m-%d') + '|' + \
                       temp_df['Склад'].astype(str) + '|' + \
                       temp_df['Штабель'].astype(str) + '|' + \
                       temp_df['Марка'].astype(str)

fires_daily['merge_key'] = fires_daily['Дата акта'].dt.strftime('%Y-%m-%d') + '|' + \
                           fires_daily['Склад'].astype(str) + '|' + \
                           fires_daily['Штабель'].astype(str) + '|' + \
                           fires_daily['Марка'].astype(str)
# Находим отсутствующие записи
missing_fires = fires_daily[~fires_daily['merge_key'].isin(temp_df['merge_key'])]

# Добавляем отсутствующие записи
if not missing_fires.empty:
    missing_data = missing_fires[['Дата акта', 'Склад', 'Штабель', 'fire', 'Вес', 'Длительность']].copy()
    # Установим 'fire' для пропущенных строк в 0 (или любое другое значение)
    missing_data['fire'] = 1  # например, 0, если пожар не произошел в эти дни
    for col in temp_df.columns:
        if col not in missing_data.columns and col not in ['merge_key', 'fire']:
            missing_data[col] = 0
    combined_df = pd.concat([temp_df, missing_data], ignore_index=True)
else:
    combined_df = temp_df.copy()

# 4. Добавляем флаги пожара и вес
combined_df = pd.merge(
    combined_df.drop('fire', axis=1, errors='ignore'),
    fires_daily[['merge_key', 'fire', 'Вес', 'Длительность', 'Марка']],  # Сохраняем столбец 'Марка'
    on='merge_key',
    how='left'
)
combined_df['fire'] = combined_df['fire'].fillna(0).astype(int)
combined_df['Только_дата'] = combined_df['Дата акта'].dt.date


# 5. Загрузка погодных данных и агрегация по дням
weather_data = pd.DataFrame()

# Пройдем по всем погодным файлам
for file in glob.glob('data/weather_data_*.csv'):
    df = pd.read_csv(file)
    df['Дата'] = pd.to_datetime(df['date'])
    df['Только_дата'] = df['Дата'].dt.date

    # Исключаем столбцы 'visibility' и 'date' для агрегации
    columns_for_aggregation = [col for col in df.columns if col not in ['visibility', 'date', 'Дата', 'Только_дата']]

    # Преобразуем все столбцы, которые участвуют в агрегации, в числовые (если это возможно)
    df[columns_for_aggregation] = df[columns_for_aggregation].apply(pd.to_numeric, errors='coerce')

    # Группировка данных по дате и вычисление статистики для всех числовых столбцов
    daily_df = df.groupby('Только_дата').agg(
        **{f"mean_{col}": (col, 'mean') for col in columns_for_aggregation},  # Среднее
        **{f"max_{col}": (col, 'max') for col in columns_for_aggregation},  # Максимум
        **{f"min_{col}": (col, 'min') for col in columns_for_aggregation}  # Минимум
    ).reset_index()

    # Округляем средние значения до 3 знаков после запятой
    mean_columns = [col for col in daily_df.columns if col.startswith('mean_')]
    daily_df[mean_columns] = daily_df[mean_columns].round(3)

    # Добавление в общий DataFrame погодных данных
    weather_data = pd.concat([weather_data, daily_df])

# 6. Загрузка данных о поступлениях на склад (supplies.csv)
supply_df = pd.read_csv('data/supplies.csv')
supply_df['ВыгрузкаНаСклад'] = pd.to_datetime(supply_df['ВыгрузкаНаСклад'])
supply_df['ПогрузкаНаСудно'] = pd.to_datetime(supply_df['ПогрузкаНаСудно'])


# 7. Добавление информации о поступлениях на склад в итоговую таблицу
def add_weight_based_on_date_and_match(row, supply_df):
    # Преобразуем Дата акта в дату без времени
    date_act = row['Дата акта'].date()

    # Получаем строки, где дата акта попадает в диапазон
    valid_supply_rows = supply_df[
        (date_act >= supply_df['ВыгрузкаНаСклад'].dt.date) &
        (date_act <= supply_df['ПогрузкаНаСудно'].dt.date) &
        (row['Склад'] == supply_df['Склад']) &
        (row['Штабель'] == supply_df['Штабель'])
        ]

    if not valid_supply_rows.empty:
        # Если нашли совпадение, возвращаем вес из первого совпавшег
        return valid_supply_rows.iloc[0]['На склад, тн']  # В данном случае "Вес" — это столбец в файле `supplies.csv`
    else:
        return 0

# Применяем к каждому ряду финальной таблицы
combined_df['Вес из поставки'] = combined_df.apply(
    add_weight_based_on_date_and_match, axis=1, supply_df=supply_df
)

combined_df['Вес из поставки'] = combined_df['Вес из поставки'].round(2)

# 8. Финальное объединение с погодой
result_df = pd.merge(
    combined_df,
    weather_data,
    left_on='Только_дата',
    right_on='Только_дата',
    how='left'
)

# 9. Удаление временных и ненужных столбцов
columns_to_drop = ['merge_key', 'Только_дата', 'Смена', 'Пикет', 'visibility', 'Марка_y', 'Вес_x', 'Длительность_x']
result_df = result_df.drop(
    columns=[col for col in columns_to_drop if col in result_df.columns],
    errors='ignore'
)

# 10. Заменить все NaN на 0 в итоговой таблице
if 'Марка_x' in result_df.columns:
    # Удаляем строки, где 'Марка' равна NaN
    result_df = result_df.dropna(subset=['Марка_x'])

# 11. Заменить все оставшиеся NaN на 0 в итоговой таблице
result_df = result_df.fillna(0)
result_df['autumn'] = 0
result_df['winter'] = 0
result_df['spring'] = 0


def get_season_flags(month):
    if month in [3, 4, 5]:
        return (0, 0, 1)  # весна
    elif month in [9, 10, 11]:
        return (1, 0, 0)  # осень
    elif month in [12, 1, 2]:
        return (0, 1, 0)  # зима
    else:
        return (0, 0, 0)  # не должно быть, но на всякий случай


result_df[['autumn', 'winter', 'spring']] = result_df['Дата акта'].dt.month.apply(
    lambda m: pd.Series(get_season_flags(m))
)

# 12. Сохранение результата
result_df.to_csv('data/learning_table.csv', index=False)
