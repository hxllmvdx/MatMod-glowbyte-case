import pandas as pd


def process_weather():
    weather_19 = pd.read_csv('data/weather_data_2019.csv', sep=',').sort_values(by='date').iloc[:, :-2]
    weather_20 = pd.read_csv('data/weather_data_2020.csv', sep=',').sort_values(by='date').iloc[:, :-2]

    weather_19['date'] = weather_19['date'].apply(lambda x: x.split(' ')[0])
    weather_20['date'] = weather_20['date'].apply(lambda x: x.split(' ')[0])

    data = {}

    for date in weather_19['date'].unique():
        temp = weather_19[weather_19['date'] == date]

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

    for date in weather_20['date'].unique():
        temp = weather_20[weather_20['date'] == date]

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


def process_fires():
    fires = pd.read_csv('data/fires.csv', sep=';').sort_values(by='Дата начала')

    fires['obj_type'] = fires['Склад'].astype(str) + '_' + fires['Штабель'].astype(str)

    fires = fires.drop(columns=['Дата составления', 'Груз', 'Вес по акту, тн', 'Дата оконч.', 'Нач.форм.штабеля',
                                'Склад', 'Штабель'])

    columns = ['date', 'obj_type']
    fires.columns = columns

    fires['date'] = fires['date'].apply(lambda x: x.split(' ')[0])

    return fires


def process_temperature():
    temperature = pd.read_csv('data/temperature.csv').sort_values(by='Дата акта')

    temperature['obj_type'] = temperature['Склад'].astype(str) + '_' + temperature['Штабель'].astype(str)

    temperature['Марка'] = temperature['Марка'].apply(lambda x: x.split('-')[0])
    temperature = temperature[temperature['Марка'] == 'A1']

    temperature = temperature.drop(columns=['Склад', 'Штабель', 'Пикет', 'Смена', 'Марка'])

    columns = ['coal_temp', 'date', 'obj_type']
    temperature.columns = columns

    return temperature


def merge_tables():
    weather, fires, temperature = process_weather(), process_fires(), process_temperature()

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


def numerate():
    df = merge_tables()

    # Преобразование даты в datetime и сортировка
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['obj_type', 'date']).reset_index(drop=True)

    # Создание групп последовательных дней для каждого объекта
    df['days_diff'] = df.groupby('obj_type')['date'].diff().dt.days.ne(1).cumsum()
    df['sequence'] = df.groupby(['obj_type', 'days_diff']).cumcount() + 1

    # Удаление вспомогательного столбца
    df = df.drop(columns='days_diff')

    return df


def delete_less_than_3():
    df = numerate()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['obj_type', 'date'])
    df['group'] = (df.groupby('obj_type')['date'].diff().dt.days.ne(1)).cumsum()

    # Расчет длины каждой группы
    group_sizes = df.groupby(['obj_type', 'group']).size().reset_index(name='group_size')

    # Объединение с исходным DataFrame и фильтрация
    df = df.merge(group_sizes, on=['obj_type', 'group'])
    df = df[df['group_size'] >= 3].drop(columns=['group', 'group_size'])

    return df


def shift_target():
    df = delete_less_than_3()

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

    return df


add_features(shift_target()).to_csv('data/learning_table.csv', sep=';', index=False)