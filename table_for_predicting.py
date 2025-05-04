import pandas as pd
import glob
from datetime import datetime, timedelta


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


def processing_work_table():
    # 2. Загрузка и обработка temperature.csv
    temp_df = pd.read_csv('data/temperature.csv')
    temp_df['Дата акта'] = pd.to_datetime(temp_df['Дата акта'])

    temp_df = process_brand_column(temp_df)

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

    temp_df['Вес из поставки'] = temp_df.apply(
        add_weight_based_on_date_and_match, axis=1, supply_df=supply_df
    )
    temp_df['Вес из поставки'] = temp_df['Вес из поставки'].round(2)
    temp_df['Дата акта'] = pd.to_datetime(temp_df['Дата акта']).dt.normalize()
    weather_data['Только_дата'] = pd.to_datetime(weather_data['Только_дата']).dt.normalize()

    # Объединение по дате
    result_df = pd.merge(
        temp_df,
        weather_data,
        left_on='Дата акта',
        right_on='Только_дата',
        how='left'
    )
    columns_to_drop = ['merge_key', 'Только_дата', 'Смена', 'Пикет', 'visibility', 'Марка_y', 'Вес_x', 'Длительность_x']
    result_df = result_df.drop(
        columns=[col for col in columns_to_drop if col in result_df.columns],
        errors='ignore'
    )

    # 10. Удаление строк с NaN в столбце 'Марка'
    if 'Марка' in result_df.columns:
        # Удаляем строки, где 'Марка' равна NaN
        result_df = result_df.dropna(subset=['Марка'])
    else:
        print("Столбец 'Марка' отсутствует в итоговой таблице")

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

    return result_df

    # 12. Сохранение результата
    # result_df.to_csv('data/working_table.csv', index=False)