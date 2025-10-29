import pandas as pd


def parsing_file(path_file):
    df = pd.read_excel(path_file)
    categories = dict()

    for index, row in df.iterrows():
        category_id = int(row['category_id'])
        name_object = row['title']

        if category_id not in categories:
            categories[category_id] = []
        categories[category_id].append(name_object)

    return categories




category_names = {1: 'Памятники и скульптуры',
                  2: 'Парки и скверы',
                  3: 'Тактильные макеты',
                  4: 'Набережные',
                  5: 'Архетектура и достопримечательности',
                  6: 'Культурные центры и досуг',
                  7: 'Музеи',
                  8: 'Театры и филармонии',
                  10: 'Стрит-арт и мозаики'}

times = {1: 15,
         2: 45,
         3: 10,
         4: 30,
         5: 20,
         6: 60,
         7: 60,
         8: 120,
         10: 10}



path = 'C:/Users/egor0/Downloads/VNDS/cultural_objects_mnn.xlsx'
main_prompt = 'Ты — помощник для создания персональных маршрутов прогулки по Нижнему Новгороду.\n'
places_prompt = '\nДАННЫЕ ДЛЯ ФОРМИРОВАНИЯ МАРШРУТА:\n'
output_prompt = '\n# ИНСТРУКЦИЯ ДЛЯ ФОРМИРОВАНИЯ ОТВЕТА: \n' \
               '1.  Создай пешеходный маршрут, логично перемещаясь от начальной точки к другим объектам. \n' \
               '2.  Включи в маршрут 3-4 места, комбинируя категории. Упоминай по пути возможные кофейни для остановки (кофейни не входят в датасет, ты можешь предложить их обобщенно, исходя из логики маршрута). \n' \
               '3.  Учитывай среднее время посещения из датасета и реалистичное время на переход между точками (5-15 минут). \n' \
               '4.  Структура ответа должна быть четкой:    \n' \
               '- **Название места и категория.**    \n' \
               '- **Обоснование выбора:** Почему мы идем именно сюда, связав с интересами пользователя. \n' \
               '- **Примерный таймлайн:** "10:00-10:20 - осмотр объекта X, 10:20-10:35 - переход к объекту Y". \n' \
               'Сформируй маршрут.'

categ = [i + 1 for i in range(10) if i != 8]
print('PARSING')
print('='*30)
data = parsing_file(path)
print('FORMING PROMPT')
print('='*30)

for c in categ:
    p = f'\nКатегория: {category_names[c]} (среднее время посещения: {times[c]} мин)\n' \
        f'Объекты, которые можно использовать: {data[c]}\n'
    places_prompt += p

main_prompt += places_prompt

interests, time, location = [input() for _ in range(3)]

user_prompt = f'ЗАПРОС ПОЛЬЗОВАТЕЛЯ:\n' \
             f'Интересы: {interests};\n' \
             f'Свободное время: {time} ч;\n' \
             f'Начальная локация: {location};'


main_prompt += user_prompt + output_prompt

print(main_prompt)
