-- Примеры SQL-запросов для проекта "Калькулятор калорий"
SELECT product, grams, calories 
FROM daily_records 
WHERE date LIKE '2025-09-22%' 
ORDER BY id DESC 
LIMIT 10;

-- Суммарная калорийность за сегодня
SELECT SUM(calories) 
FROM daily_records 
WHERE date LIKE '2025-09-22%';

-- Очистка истории за сегодня
DELETE FROM daily_records 
WHERE date LIKE '2025-09-22%';

-- Получение всех записей за сегодня
SELECT * 
FROM daily_records 
WHERE date LIKE '2025-09-22%';

-- Получение суммарной калорийности по каждому продукту
SELECT product, SUM(calories) as total_calories
FROM daily_records
WHERE date LIKE '2025-09-22%'
GROUP BY product;