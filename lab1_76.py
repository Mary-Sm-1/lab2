"""
import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import StringIO

# Загрузка
url = "https://raw.githubusercontent.com/dm-fedorov/python_basic/master/data/opendata.stat"
df = pd.read_csv(StringIO(requests.get(url).text))

# Обработка даты
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year

# Фильтрация
filtered = df[(df['region'] == 'Забайкальский край') & (df['year'] == 2018)]

if not filtered.empty:
    # Среднее значение
    avg = filtered['value'].mean()
    print(f"Среднее значение: {avg:.2f}")
    
    # График
    filtered = filtered.sort_values('date')
    plt.figure(figsize=(10, 6))
    plt.plot(filtered['date'], filtered['value'], marker='o')
    for date, value in zip(filtered['date'], filtered['value']):
        date_str = date.strftime('%Y-%m-%d')
        print(f"{date_str:<12} | {value:>10.2f}")
    plt.title(f'{filtered["name"].iloc[0]} в Забайкальском крае, 2018')
    plt.xlabel('Дата')
    plt.ylabel('Значение')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('graph.png')
    plt.show()
else:
    print("Данные не найдены!")
"""
import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import StringIO

# Загрузка данных
url = "https://raw.githubusercontent.com/dm-fedorov/python_basic/master/data/opendata.stat"
df = pd.read_csv(StringIO(requests.get(url).text))

# Преобразование даты
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

# Фильтрация данных: пенсии в Забайкальском крае за 2018 год
# Ищем показатели, связанные с пенсиями
pension_keywords = ['пенси', 'пенс', 'пенсион', 'pension', 'выплат пенс']
mask_region = df['region'] == 'Забайкальский край'
mask_year = df['year'] == 2018

# Фильтруем по региону и году
filtered = df[mask_region & mask_year].copy()

# Ищем строки, содержащие ключевые слова о пенсиях
pension_mask = filtered['name'].str.contains('|'.join(pension_keywords), case=False, na=False)

if pension_mask.any():
    pension_data = filtered[pension_mask].copy()
    
    # Преобразуем значение в числовой формат
    pension_data['value'] = pd.to_numeric(pension_data['value'], errors='coerce')
    """
    print("=" * 70)
    print("НАЙДЕННЫЕ ПОКАЗАТЕЛИ ПО ПЕНСИЯМ:")
    print("=" * 70)
    print(f"Уникальные показатели: {pension_data['name'].unique()}")
    print(f"Количество записей: {len(pension_data)}")
    print()
    """
    # Группируем по дате и вычисляем среднее значение пенсии для каждой даты
    daily_pension = pension_data.groupby('date')['value'].mean().reset_index()
    daily_pension = daily_pension.sort_values('date')
    
    # Вычисляем общее среднее значение
    overall_avg = daily_pension['value'].mean()
    
    print(f"ОБЩЕЕ СРЕДНЕЕ ЗНАЧЕНИЕ ПЕНСИИ ЗА 2018 ГОД: {overall_avg:.2f}")
    print()
    """
    print("СРЕДНИЕ ЗНАЧЕНИЯ ПО ДАТАМ:")
    print("-" * 40)
    print(f"{'Дата':<12} | {'Средняя пенсия':<15}")
    print("-" * 40)
    
    for _, row in daily_pension.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d')
        print(f"{date_str:<12} | {row['value']:>15.2f}")
    
    print("-" * 40)
    print(f"Всего уникальных дат: {len(daily_pension)}")
    print("=" * 70)
    """
    # Построение графика
    plt.figure(figsize=(14, 8))
    
    # График средних значений пенсии по датам
    plt.plot(daily_pension['date'], daily_pension['value'], 
             marker='o', linestyle='-', linewidth=2, markersize=8,
             color='darkblue', alpha=0.8, label='Средняя пенсия по дате')
    
    # Линия среднего значения
    plt.axhline(y=overall_avg, color='red', linestyle='--', linewidth=2,
                alpha=0.7, label=f'Общее среднее: {overall_avg:.2f}')
    
    # Настройки графика
    plt.title('Изменение среднего значения пенсии в Забайкальском крае, 2018 год',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Среднее значение пенсии', fontsize=12)
    
    # Сетка
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Легенда
    plt.legend(fontsize=11)
    
    # Форматирование дат на оси X
    plt.gcf().autofmt_xdate()
    
    # Добавление значений над точками
    for i, (date, value) in enumerate(zip(daily_pension['date'], daily_pension['value'])):
        plt.annotate(f'{value:.1f}', 
                     xy=(date, value), 
                     xytext=(0, 10),
                     textcoords='offset points',
                     ha='center',
                     fontsize=9,
                     color='darkblue')
    
    plt.tight_layout()
    
    # Сохранение графика
    plt.savefig('pension_trend_2018.png', dpi=150, bbox_inches='tight')
    
    # Показать график
    plt.show()
    
else:
    print("=" * 70)
    print("ВНИМАНИЕ: Данные о пенсиях не найдены!")
    print("=" * 70)
    
    # Покажем, какие показатели вообще есть в данных
    print("Доступные показатели в Забайкальском крае за 2018 год:")
    print("-" * 50)
    
    unique_indicators = filtered['name'].unique()
    for i, indicator in enumerate(unique_indicators[:20]):  # Покажем первые 20
        print(f"{i+1}. {indicator}")
    
    if len(unique_indicators) > 20:
        print(f"... и еще {len(unique_indicators) - 20} показателей")
    
    print("-" * 50)
    print("\nСовет: Попробуйте найти данные по другим ключевым словам")