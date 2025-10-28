
Схема базы данных
Таблицы
categories
id (PK)

name VARCHAR(100)

keywords TEXT[]

avg_visit_duration INTEGER

places
id (PK)

title VARCHAR(255)

address TEXT

latitude DECIMAL(10,8)

longitude DECIMAL(11,8)

category_id (FK)

user_requests
id (PK, SERIAL)

user_interests TEXT

selected_places_ids INTEGER[]

created_at TIMESTAMP
