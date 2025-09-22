import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

food_items = {
    "Яблоко": 52, "Банан": 89, "Апельсин": 47, "Груша": 57, "Виноград": 69,
    "Клубника": 32, "Арбуз": 30, "Дыня": 34, "Персик": 39, "Абрикос": 48,
    "Слива": 46, "Вишня": 52, "Черешня": 50, "Киви": 61, "Ананас": 50,
    "Манго": 60, "Гранат": 83, "Хлеб белый": 265, "Хлеб черный": 250,
    "Хлеб цельнозерновой": 240, "Батон": 260, "Багет": 290, "Лаваш": 275,
    "Молоко": 42, "Кефир": 41, "Йогурт натуральный": 60, "Сметана": 206,
    "Творог": 121, "Сыр": 402, "Брынза": 260, "Моцарелла": 280, "Сливочное масло": 717,
    "Яйцо": 155, "Яичный белок": 52, "Яичный желток": 352,
    "Картофель": 77, "Морковь": 41, "Помидор": 18, "Огурец": 15,
    "Капуста белокочанная": 28, "Капуста цветная": 30, "Брокколи": 34,
    "Лук": 40, "Чеснок": 149, "Свекла": 43, "Тыква": 22, "Кабачок": 24,
    "Баклажан": 24, "Перец болгарский": 27, "Шпинат": 23, "Сельдерей": 12,
    "Курица": 239, "Индейка": 190, "Говядина": 250, "Свинина": 242,
    "Баранина": 209, "Утка": 308, "Гусь": 364, "Кролик": 183,
    "Рис": 130, "Гречка": 132, "Овсянка": 88, "Пшено": 135,
    "Макароны": 131, "Спагетти": 158, "Лапша": 138
}

#Класс для работы с бд
class CalorieDatabase:
    def __init__(self):
        self.connection = sqlite3.connect('calorie_tracker.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        #Создание таблицы в базе данных
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                food_name TEXT NOT NULL,
                weight_grams REAL NOT NULL,
                food_calories REAL NOT NULL,
                total_calories REAL NOT NULL
            )
        ''')
        self.connection.commit()

    def add_food_record(self, food_name, weight_grams, food_calories, total_calories):
        #Добавление записи о еде в базу данных
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO food_history (date, food_name, weight_grams, food_calories, total_calories) VALUES (?, ?, ?, ?, ?)",
            (current_time, food_name, weight_grams, food_calories, total_calories)
        )
        self.connection.commit()

    def get_today_food(self):
        #Получение списка еды за сегодня
        today_date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            "SELECT food_name, weight_grams, food_calories FROM food_history WHERE date LIKE ? ORDER BY id DESC LIMIT 10",
            (f"{today_date}%",)
        )
        return self.cursor.fetchall()

    def get_today_total_calories(self):
        #Получение суммы калорий за сегодня
        today_date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            "SELECT SUM(food_calories) FROM food_history WHERE date LIKE ?",
            (f"{today_date}%",)
        )
        result = self.cursor.fetchone()
        return result[0] if result[0] else 0

    def clear_today_food(self):
        #Удаление записей за сегодня
        today_date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            "DELETE FROM food_history WHERE date LIKE ?",
            (f"{today_date}%",)
        )
        self.connection.commit()
        return self.cursor.rowcount

calorie_history = []
food_history = []
current_calories = 0
daily_limit = 2000  # стандартная норма

#Создание бд
db = CalorieDatabase()

#Расчет дневной нормы калорий
def calculate_daily_calories():
    global daily_limit, current_calories
    try:
        user_weight = float(weight_input.get())
        user_height = float(height_input.get())
        user_age = int(age_input.get())
        user_gender = gender_input.get()
        user_goal = goal_input.get()
        user_activity = activity_input.get()

        #Расчет базового метаболизма
        if user_gender == "Мужчина":
            base_metabolism = 88.36 + (13.4 * user_weight) + (4.8 * user_height) - (5.7 * user_age)
        else:
            base_metabolism = 447.6 + (9.2 * user_weight) + (3.1 * user_height) - (4.3 * user_age)

        #Учет уровня активности
        activity_multipliers = {
            "Сидячий (офис)": 1.2,
            "Низкая активность": 1.375,
            "Средняя активность": 1.55,
            "Высокая активность": 1.725,
            "Очень высокая активность": 1.9
        }
        daily_limit = base_metabolism * activity_multipliers.get(user_activity, 1.55)

        #Корректировка по цели
        if user_goal == "Похудение":
            daily_limit -= 500
        elif user_goal == "Набор массы":
            daily_limit += 500

        #Обновление интерфейса
        daily_label.config(text=f"Дневная норма калорий: {daily_limit:.0f} ккал")
        current_calories = db.get_today_total_calories()
        calorie_history.clear()
        food_history.clear()

        # Загрузка истории за сегодня
        today_food = db.get_today_food()
        for food_name, weight_grams, food_calories in today_food:
            food_history.append(f"{food_name} ({weight_grams} г) = {food_calories:.1f} ккал")

        update_interface()

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите правильные числа!")

#Добавление продукта
def add_food_item():
    global current_calories
    selected_food = food_input.get()
    food_weight = weight_food_input.get()

    if selected_food not in food_items:
        messagebox.showerror("Ошибка", "Этот продукт не найден в списке!")
        return

    try:
        food_weight = float(food_weight)
    except ValueError:
        messagebox.showerror("Ошибка", "Введите правильный вес в граммах!")
        return

    #Расчет калорий
    calories_in_food = food_items[selected_food] * food_weight / 100
    current_calories += calories_in_food

    food_history.append(f"{selected_food} ({food_weight} г) = {calories_in_food:.1f} ккал")
    calorie_history.append(current_calories)

    #Сохранение в бд
    db.add_food_record(selected_food, food_weight, calories_in_food, current_calories)

    update_interface()

#Обновление интерфейса
def update_interface():
    calories_left = daily_limit - current_calories
    result_label.config(text=f"Общая калорийность: {current_calories:.1f} ккал\n"
                             f"Осталось до нормы: {calories_left:.1f} ккал")
    history_label.config(text="\n".join(food_history[-10:]))

    # Статистика из базы данных
    today_total = db.get_today_total_calories()
    stats_label.config(text=f"📊 Сегодня съедено: {today_total:.1f} ккал")

    if current_calories > daily_limit:
        advice_label.config(text="⚠ Вы превысили дневную норму!", fg="red")
    else:
        advice_label.config(text="Норма в пределах допустимого", fg="green")

#Показать график
def show_calorie_chart():
    if not calorie_history:
        messagebox.showinfo("График", "Сначала добавьте продукты!")
        return
    plt.figure(figsize=(8, 4))
    plt.plot(range(1, len(calorie_history) + 1), calorie_history, marker="o", color="blue")
    plt.axhline(daily_limit, color="red", linestyle="--", label="Дневная норма")
    plt.title("Изменение общей калорийности")
    plt.xlabel("Количество добавленных продуктов")
    plt.ylabel("Калории (ккал)")
    plt.legend()
    plt.grid(True)
    plt.show()

#Показать историю питания
def show_food_history():
    history = db.get_today_food()
    if not history:
        messagebox.showinfo("История", "За сегодня еще нет записей")
        return

    history_text = "📅 История за сегодня:\n\n"
    for i, (food_name, weight_grams, food_calories) in enumerate(history, 1):
        history_text += f"{i}. {food_name} - {weight_grams}г = {food_calories:.1f} ккал\n"

    messagebox.showinfo("История питания", history_text)

#Очистка истории
def clear_food_history():
    answer = messagebox.askyesno(
        "Очистка истории",
        "Удалить все записи за сегодня?",
        icon='question'
    )

    if answer:
        deleted_count = db.clear_today_food()
        messagebox.showinfo("Очистка истории", f"Удалено записей: {deleted_count}")

        global current_calories
        current_calories = 0
        calorie_history.clear()
        food_history.clear()
        update_interface()

#Создание интерфейса
app = tk.Tk()
app.title("Калькулятор калорий")
app.geometry("500x600")

#Заголовок
title = tk.Label(app, text="Калькулятор калорий", font=("Arial", 14, "bold"))
title.pack(pady=10)

#Поля для ввода роста, веса, возраста
input_frame = tk.Frame(app)
input_frame.pack(pady=5)
tk.Label(input_frame, text="Вес (кг)").grid(row=0, column=0)
tk.Label(input_frame, text="Рост (см)").grid(row=0, column=1)
tk.Label(input_frame, text="Возраст").grid(row=0, column=2)

weight_input = tk.StringVar()
weight_entry = tk.Entry(input_frame, textvariable=weight_input, width=5)
weight_entry.grid(row=1, column=0)

height_input = tk.StringVar()
height_entry = tk.Entry(input_frame, textvariable=height_input, width=5)
height_entry.grid(row=1, column=1)

age_input = tk.StringVar()
age_entry = tk.Entry(input_frame, textvariable=age_input, width=5)
age_entry.grid(row=1, column=2)

#Выбор пола, цели, активности
choice_frame = tk.Frame(app)
choice_frame.pack(pady=5)

gender_input = tk.StringVar(value="Мужчина")
gender_combo = ttk.Combobox(choice_frame, textvariable=gender_input, values=["Мужчина", "Женщина"], width=10)
gender_combo.grid(row=0, column=0, padx=5)

goal_input = tk.StringVar(value="Поддержание веса")
goal_combo = ttk.Combobox(choice_frame, textvariable=goal_input,
                          values=["Поддержание веса", "Похудение", "Набор массы"], width=15)
goal_combo.grid(row=0, column=1, padx=5)

activity_input = tk.StringVar(value="Средняя активность")
activity_combo = ttk.Combobox(choice_frame, textvariable=activity_input, values=[
    "Сидячий (офис)", "Низкая активность", "Средняя активность", "Высокая активность", "Очень высокая активность"],
                              width=18)
activity_combo.grid(row=0, column=2, padx=5)

calc_button = tk.Button(choice_frame, text="Рассчитать норму", command=calculate_daily_calories)
calc_button.grid(row=0, column=3, padx=5)

#Метка дневной нормы
daily_label = tk.Label(app, text=f"Дневная норма калорий: {daily_limit:.0f} ккал", font=("Arial", 12))
daily_label.pack(pady=5)

#Статистика
stats_label = tk.Label(app, text="📊 Сегодня съедено: 0 ккал", font=("Arial", 10), fg="blue")
stats_label.pack(pady=2)

#Выбор продукта
food_input = tk.StringVar()
food_combo = ttk.Combobox(app, textvariable=food_input, width=30)
food_combo['values'] = sorted(list(food_items.keys()))
food_combo.pack(pady=5)
food_combo.set("Выберите продукт")

weight_food_input = tk.StringVar()
weight_food_entry = tk.Entry(app, textvariable=weight_food_input, width=30)
weight_food_entry.pack(pady=5)
weight_food_entry.insert(0, "Вес в граммах")

add_food_button = tk.Button(app, text="Добавить продукт", command=add_food_item)
add_food_button.pack(pady=10)

#Кнопки истории
history_buttons_frame = tk.Frame(app)
history_buttons_frame.pack(pady=5)

show_history_button = tk.Button(history_buttons_frame, text="📋 Показать историю", command=show_food_history)
show_history_button.grid(row=0, column=0, padx=5)

clear_history_button = tk.Button(history_buttons_frame, text="🗑️ Очистить историю", command=clear_food_history,
                                 bg="#ffcccc")
clear_history_button.grid(row=0, column=1, padx=5)

#Результаты
result_label = tk.Label(app, text="Общая калорийность: 0 ккал", font=("Arial", 12))
result_label.pack(pady=5)

history_label = tk.Label(app, text="", font=("Arial", 10), justify="left")
history_label.pack(pady=5)

advice_label = tk.Label(app, text="", font=("Arial", 12, "italic"))
advice_label.pack(pady=5)

chart_button = tk.Button(app, text="Показать график калорий", command=show_calorie_chart)
chart_button.pack(pady=10)

app.mainloop()