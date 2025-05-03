import pandas as pd
import glob
from datetime import datetime, timedelta

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

# Создаем полный список дней с пожарами
fire_days_all = []
for _, row in fires_df.iterrows():
    days = expand_date_range(row['Дата начала'], row['Дата оконч.'])
    for day in days:
        fire_days_all.append({
            'Дата акта': datetime.combine(day, datetime.min.time()),
            'Склад': row['Склад'],
            'Штабель': row['Штабель'],
            'fire': 1
        })

fires_daily = pd.DataFrame(fire_days_all).drop_duplicates()

# 2. Загрузка и обработка temperature.csv
temp_df = pd.read_csv('data/temperature.csv')
temp_df['Дата акта'] = pd.to_datetime(temp_df['Дата акта'])

# 3. Объединение данных о пожарах с temperature.csv
temp_df['merge_key'] = temp_df['Дата акта'].dt.strftime('%Y-%m-%d') + '|' + \
                      temp_df['Склад'].astype(str) + '|' + \
                      temp_df['Штабель'].astype(str)

fires_daily['merge_key'] = fires_daily['Дата акта'].dt.strftime('%Y-%m-%d') + '|' + \
                          fires_daily['Склад'].astype(str) + '|' + \
                          fires_daily['Штабель'].astype(str)

# Находим отсутствующие записи
missing_fires = fires_daily[~fires_daily['merge_key'].isin(temp_df['merge_key'])]

# Добавляем отсутствующие записи
if not missing_fires.empty:
    missing_data = missing_fires[['Дата акта', 'Склад', 'Штабель', 'fire']].copy()
    for col in temp_df.columns:
        if col not in missing_data.columns and col not in ['merge_key', 'fire']:
            missing_data[col] = None
    combined_df = pd.concat([temp_df, missing_data], ignore_index=True)
else:
    combined_df = temp_df.copy()

# 4. Добавляем флаги пожара
combined_df = pd.merge(
    combined_df.drop('fire', axis=1, errors='ignore'),
    fires_daily[['merge_key', 'fire']],
    on='merge_key',
    how='left'
)
combined_df['fire'] = combined_df['fire'].fillna(0).astype(int)

# 5. Загрузка погодных данных (один раз в конце)
weather_data = pd.DataFrame()
for file in glob.glob('data/weather_data_*.csv'):
    df = pd.read_csv(file)
    df['Дата'] = pd.to_datetime(df['date'])
    df['Только_дата'] = df['Дата'].dt.date
    daily_df = df.groupby('Только_дата').mean(numeric_only=True).round(3).reset_index()
    weather_data = pd.concat([weather_data, daily_df])

# 6. Финальное объединение с погодой
combined_df['Только_дата'] = combined_df['Дата акта'].dt.date
result_df = pd.merge(
    combined_df,
    weather_data,
    left_on='Только_дата',
    right_on='Только_дата',
    how='left'
)

# 7. Удаление временных и ненужных столбцов
columns_to_drop = ['merge_key', 'Только_дата', 'Смена', 'Пикет', 'visibility', "weather_code"]
result_df = result_df.drop(
    columns=[col for col in columns_to_drop if col in result_df.columns],
    errors='ignore'
)

# 8. Сохранение результата
result_df.to_csv('final_result.csv', index=False)