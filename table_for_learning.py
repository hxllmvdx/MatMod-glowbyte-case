import pandas as pd
from os import getcwd


def process_weather(path):
    weather = pd.read_csv(path, sep=',').sort_values(by='date').iloc[:, :-2]

    weather['date'] = weather['date'].apply(lambda x: x.split(' ')[0])

    data = {}

    for date in weather['date'].unique():
        temp = weather[weather['date'] == date]

        temp_max = temp['t'].max()
        temp_mean = temp['t'].mean()

        humidity_max = temp['humidity'].max()
        humidity_mean = temp['humidity'].mean()

        precipitation = temp['precipitation'].max()

        v_mean = temp['v_avg'].mean()
        v_max = temp['v_max'].mean()

        p_mean = temp['p'].mean()
        p_max = temp['p'].max()

        data['date'] = data.get('date', []) + [date]
        data['temp_max'] = data.get('temp_max', []) + [temp_max]
        data['temp_mean'] = data.get('temp_mean', []) + [temp_mean]
        data['humidity_max'] = data.get('humidity_max', []) + [humidity_max]
        data['humidity_mean'] = data.get('humidity_mean', []) + [humidity_mean]
        data['precipitation'] = data.get('precipitation', []) + [precipitation]
        data['v_mean'] = data.get('v_mean', []) + [v_mean]
        data['v_max'] = data.get('v_max', []) + [v_max]
        data['p_mean'] = data.get('p_mean', []) + [p_mean]
        data['p_max'] = data.get('p_max', []) + [p_max]

    return pd.DataFrame(data)


def process_fires(path):
    try:
        fires = pd.read_csv(path, sep=',').sort_values(by='Дата начала')
    except:
        pass

    try:
        fires = pd.read_csv(path, sep=';').sort_values(by='Дата начала')
    except:
        pass

    fires['obj_type'] = fires['Склад'].astype(str) + '_' + fires['Штабель'].astype(str)

    fires = fires.drop(columns=['Дата составления', 'Груз', 'Вес по акту, тн', 'Дата оконч.', 'Нач.форм.штабеля',
                                'Склад', 'Штабель'])

    columns = ['date', 'obj_type']
    fires.columns = columns

    fires['date'] = fires['date'].apply(lambda x: x.split(' ')[0])

    return fires


def process_temperature(path):
    temperature = pd.read_csv(path).sort_values(by='Дата акта')

    temperature['obj_type'] = temperature['Склад'].astype(str) + '_' + temperature['Штабель'].astype(str)

    temperature['Марка'] = temperature['Марка'].apply(lambda x: x.split('-')[0])
    temperature = temperature[temperature['Марка'] == 'A1']

    temperature = temperature.drop(columns=['Склад', 'Штабель', 'Пикет', 'Смена', 'Марка'])

    columns = ['coal_temp', 'date', 'obj_type']
    temperature.columns = columns

    return temperature


def merge_tables(*paths):
    weathers = []
    paths = paths[0]

    for path in paths:
        if 'weather' in path:
            paths = paths[paths.index(path) + 1:]
            weathers.append(process_weather(path))

    weather = pd.concat(weathers, axis=0)

    fires, temperature = process_fires(paths[0]), process_temperature(paths[1])

    filter_date = temperature['date'].min()

    fires = fires[fires['date'] >= filter_date]

    begin_date = '2020-05-11'

    temperature = temperature[temperature['date'] >= begin_date]

    last_date = temperature['date'].max()
    weather = weather[weather['date'] <= last_date]

    data = {}

    for i in range(3413):
        temp1 = temperature.iloc[i]
        temp2 = temperature[temperature['date'] == temp1['date']]
        temp2 = temp2[temp2['obj_type'] == temp1['obj_type']]
        temp3 = weather[weather['date'] == temp1['date']]
        targets = fires[fires['date'] == temp1['date']]
        targets = targets[targets['obj_type'] == temp1['obj_type']]

        data['date'] = data.get('date', []) + [temp1['date']]
        data['obj_type'] = data.get('obj_type', []) + [temp1['obj_type']]
        data['coal_temp'] = data.get('coal_temp', []) + [temp2['coal_temp'].max()]
        data['temp_max'] = data.get('temp_max', []) + [temp3['temp_max'].values[0]]
        data['temp_mean'] = data.get('temp_mean', []) + [temp3['temp_mean'].values[0]]
        data['humidity_max'] = data.get('humidity_max', []) + [temp3['humidity_max'].values[0]]
        data['humidity_mean'] = data.get('humidity_mean', []) + [temp3['humidity_mean'].values[0]]
        data['precipitation'] = data.get('precipitation', []) + [temp3['precipitation'].values[0]]
        data['v_mean'] = data.get('v_mean', []) + [temp3['v_mean'].values[0]]
        data['v_max'] = data.get('v_max', []) + [temp3['v_max'].values[0]]
        data['p_mean'] = data.get('p_mean', []) + [temp3['p_mean'].values[0]]
        data['p_max'] = data.get('p_max', []) + [temp3['p_max'].values[0]]

        month = temp1['date'].split('-')[1]

        if month == '05':
            data['spring'] = data.get('spring', []) + [1]
            data['summer'] = data.get('summer', []) + [0]
            data['autumn'] = data.get('autumn', []) + [0]
        elif month in ['06', '07', '08']:
            data['spring'] = data.get('spring', []) + [0]
            data['summer'] = data.get('summer', []) + [1]
            data['autumn'] = data.get('autumn', []) + [0]
        else:
            data['spring'] = data.get('spring', []) + [0]
            data['summer'] = data.get('summer', []) + [0]
            data['autumn'] = data.get('autumn', []) + [1]

        event = 0 if not len(targets.values) else 1
        data['target'] = data.get('target', []) + [event]

    return pd.DataFrame(data).sort_values(by=['obj_type', 'date']).drop_duplicates()


def numerate(df):
    # Преобразование даты в datetime и сортировка
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['obj_type', 'date']).reset_index(drop=True)

    # Создание групп последовательных дней для каждого объекта
    df['days_diff'] = df.groupby('obj_type')['date'].diff().dt.days.ne(1).cumsum()
    df['sequence'] = df.groupby(['obj_type', 'days_diff']).cumcount() + 1

    # Удаление вспомогательного столбца
    df = df.drop(columns='days_diff')

    return df


def delete_less_than_3(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['obj_type', 'date'])
    df['group'] = (df.groupby('obj_type')['date'].diff().dt.days.ne(1)).cumsum()

    # Расчет длины каждой группы
    group_sizes = df.groupby(['obj_type', 'group']).size().reset_index(name='group_size')

    # Объединение с исходным DataFrame и фильтрация
    df = df.merge(group_sizes, on=['obj_type', 'group'])
    df = df[df['group_size'] >= 3].drop(columns=['group', 'group_size'])

    return df


def shift_target(df):
    df['date'] = pd.to_datetime(df['date'])

    # Шаг 1: Создание групп для каждого объекта с учетом разрывов в датах и target=1
    df = df.sort_values(by=['obj_type', 'date'])

    # Группировка по разрывам в датах (более 1 дня)
    df['date_diff'] = df.groupby('obj_type')['date'].diff().dt.days.fillna(0)
    df['gap'] = (df['date_diff'] != 1).astype(int)
    df['group'] = df.groupby(['obj_type', df['gap'].cumsum()]).ngroup()

    # Шаг 3: Сдвиг target на 3 дня назад и фильтрация
    df['shifted_target'] = df.groupby(['obj_type', 'group'])['target'].shift(-3)
    df = df.dropna(subset=['shifted_target'])

    # Удаление вспомогательных столбцов
    df = df.drop(columns=['date_diff', 'gap'])

    return df


# Создаем лаги внутри каждой группы (obj_type + group) и заполняем пропуски средним по группе
def create_lag_with_fill(df, column, lag=1):
    return (
        df.groupby(['obj_type', 'group'])[column]
        .shift(lag)
        .fillna(
            df.groupby(['obj_type', 'group'])[column]
            .transform('mean')
        )
    )


def add_features(df):
    # 1. Сортировка данных внутри групп
    df = df.sort_values(by=['obj_type', 'group', 'date'])

    # 2. Расчет скользящего среднего с окном 3 дня внутри каждой группы
    window_size = 3  # Можно изменить размер окна
    df['coal_temp_rolling_mean'] = (
        df.groupby(['obj_type', 'group'])['coal_temp']
        .transform(lambda x: x.rolling(window=window_size, min_periods=1).mean())
    )

    # 3. Заполнение пропусков (если нужно)
    df['coal_temp_rolling_mean'] = df['coal_temp_rolling_mean'].ffill()

    group_mean = df.groupby("obj_type")["coal_temp"].transform("mean")
    df["coal_temp_deviation"] = df["coal_temp"] - group_mean

    df["month"] = df["date"].dt.month

    # Дисперсия с ddof=0 (для выборки)
    df['coal_temp_var'] = (
        df.groupby(['obj_type', 'group'])['coal_temp']
        .transform(lambda x: x.var(ddof=0)))

    df['coal_temp_p_mean'] = df['coal_temp'] * df['p_mean']

    # Пример: добавляем лаги температуры угля за 1 и 3 дня
    df['coal_temp_lag1d'] = create_lag_with_fill(df, 'coal_temp', lag=1)
    df['coal_temp_lag2d'] = create_lag_with_fill(df, 'coal_temp', lag=2)
    df['coal_temp_lag3d'] = create_lag_with_fill(df, 'coal_temp', lag=3)

    return df


def create_predict_table(*paths):
    weathers = []

    for path in paths:
        if 'weather' in path:
            paths = paths[paths.index(path) + 1:]
            weathers.append(process_weather(path))

    weather = pd.concat(weathers, axis=0)
    temperature = process_fires(paths[0])

    begin_date = temperature['date'].min()
    end_date = temperature['date'].max()

    weather = weather.loc[weather.date >= begin_date]
    weather = weather.loc[weather.date <= end_date]

    data = {}

    for i in range(3413):
        temp1 = temperature.iloc[i]
        temp2 = temperature[temperature['date'] == temp1['date']]
        temp2 = temp2[temp2['obj_type'] == temp1['obj_type']]
        temp3 = weather[weather['date'] == temp1['date']]

        data['date'] = data.get('date', []) + [temp1['date']]
        data['obj_type'] = data.get('obj_type', []) + [temp1['obj_type']]
        data['coal_temp'] = data.get('coal_temp', []) + [temp2['coal_temp'].max()]
        data['temp_max'] = data.get('temp_max', []) + [temp3['temp_max'].values[0]]
        data['temp_mean'] = data.get('temp_mean', []) + [temp3['temp_mean'].values[0]]
        data['humidity_max'] = data.get('humidity_max', []) + [temp3['humidity_max'].values[0]]
        data['humidity_mean'] = data.get('humidity_mean', []) + [temp3['humidity_mean'].values[0]]
        data['precipitation'] = data.get('precipitation', []) + [temp3['precipitation'].values[0]]
        data['v_mean'] = data.get('v_mean', []) + [temp3['v_mean'].values[0]]
        data['v_max'] = data.get('v_max', []) + [temp3['v_max'].values[0]]
        data['p_mean'] = data.get('p_mean', []) + [temp3['p_mean'].values[0]]
        data['p_max'] = data.get('p_max', []) + [temp3['p_max'].values[0]]

        month = temp1['date'].split('-')[1]

        if month == '05':
            data['spring'] = data.get('spring', []) + [1]
            data['summer'] = data.get('summer', []) + [0]
            data['autumn'] = data.get('autumn', []) + [0]
        elif month in ['06', '07', '08']:
            data['spring'] = data.get('spring', []) + [0]
            data['summer'] = data.get('summer', []) + [1]
            data['autumn'] = data.get('autumn', []) + [0]
        else:
            data['spring'] = data.get('spring', []) + [0]
            data['summer'] = data.get('summer', []) + [0]
            data['autumn'] = data.get('autumn', []) + [1]

    df = pd.DataFrame(data)
    df = numerate(df)
    df = delete_less_than_3(df)
    df = add_features(df)

    df.to_csv('data/pred_table.table.csv')


def create_learning_table(*paths):
    df = add_features(shift_target(delete_less_than_3(numerate(merge_tables(paths)))))

    df.to_csv('data/learning_table.csv', index=False)


