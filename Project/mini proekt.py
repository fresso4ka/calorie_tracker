import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

products = {
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

#БД
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('calorie_tracker.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                product TEXT NOT NULL,
                grams REAL NOT NULL,
                calories REAL NOT NULL,
                total_calories REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def save_record(self, product, grams, calories, total_calories):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO daily_records (date, product, grams, calories, total_calories) VALUES (?, ?, ?, ?, ?)",
            (date, product, grams, calories, total_calories)
        )
        self.conn.commit()

    def get_today_history(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            "SELECT product, grams, calories FROM daily_records WHERE date LIKE ? ORDER BY id DESC LIMIT 10",
            (f"{today}%",)
        )
        return self.cursor.fetchall()

    def get_total_today_calories(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            "SELECT SUM(calories) FROM daily_records WHERE date LIKE ?",
            (f"{today}%",)
        )
        result = self.cursor.fetchone()
        return result[0] if result[0] else 0

    def clear_today_history(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            "DELETE FROM daily_records WHERE date LIKE ?",
            (f"{today}%",)
        )
        self.conn.commit()
        return self.cursor.rowcount  #Возвращает кол-во удаленных записей

#Данные трекера
calories_list = []
products_list = []
total_calories = 0
daily_calories = 2000  # по умолчанию

#Инициализация бд
db = DatabaseManager()

#Расчет BMR и дневной нормы с учетом активности
def calculate_bmr():
    global daily_calories, total_calories
    try:
        weight = float(weight_var.get())
        height = float(height_var.get())
        age = int(age_var.get())
        sex = sex_var.get()
        goal = goal_var.get()
        activity_level = activity_var.get()

        if sex == "Мужчина":
            bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
        else:
            bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)

        activity_factors = {
            "Сидячий (офис)": 1.2,
            "Низкая активность": 1.375,
            "Средняя активность": 1.55,
            "Высокая активность": 1.725,
            "Очень высокая активность": 1.9
        }
        daily_calories = bmr * activity_factors.get(activity_level, 1.55)

        if goal == "Похудение":
            daily_calories -= 500
        elif goal == "Набор массы":
            daily_calories += 500

        daily_label.config(text=f"Дневная норма калорий: {daily_calories:.0f} ккал")
        total_calories = db.get_total_today_calories()  #Загружаем из бд
        calories_list.clear()
        products_list.clear()

        #Загружаем историю за сегодня
        today_history = db.get_today_history()
        for product, grams, calories in today_history:
            products_list.append(f"{product} ({grams} г) = {calories:.1f} ккал")

        update_display()

    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные числовые значения!")

#Добавление продукта
def add_product():
    global total_calories
    prod_name = product_var.get()
    grams = grams_var.get()

    if prod_name not in products:
        messagebox.showerror("Ошибка", "Такого продукта нет в списке!")
        return

    try:
        grams = float(grams)
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректное количество грамм!")
        return

    cal = products[prod_name] * grams / 100
    total_calories += cal

    products_list.append(f"{prod_name} ({grams} г) = {cal:.1f} ккал")
    calories_list.append(total_calories)

    #Сохранение в бд
    db.save_record(prod_name, grams, cal, total_calories)

    update_display()

def update_display():
    result_label.config(text=f"Общая калорийность: {total_calories:.1f} ккал\n"
                             f"Остаток до нормы: {daily_calories - total_calories:.1f} ккал")
    tracker_label.config(text="\n".join(products_list[-10:]))

    #Статистика из бд
    today_total = db.get_total_today_calories()
    db_stats_label.config(text=f"📊 Сегодня съедено: {today_total:.1f} ккал")

    if total_calories > daily_calories:
        advice_label.config(text="⚠ Вы превысили дневную норму!", fg="red")
    else:
        advice_label.config(text="Норма в пределах допустимого", fg="green")

#График
def show_graph():
    if not calories_list:
        messagebox.showinfo("График", "Сначала добавьте продукт!")
        return
    plt.figure(figsize=(8, 4))
    plt.plot(range(1, len(calories_list) + 1), calories_list, marker="o", color="blue")
    plt.axhline(daily_calories, color="red", linestyle="--", label="Норма калорий")
    plt.title("Изменение общей калорийности")
    plt.xlabel("Количество добавленных продуктов")
    plt.ylabel("Общая калорийность (ккал)")
    plt.legend()
    plt.grid(True)
    plt.show()

#Показать историю из бд
def show_db_history():
    history = db.get_today_history()
    if not history:
        messagebox.showinfo("История", "За сегодня еще нет записей")
        return

    history_text = "📅 История за сегодня:\n\n"
    for i, (product, grams, calories) in enumerate(history, 1):
        history_text += f"{i}. {product} - {grams}г = {calories:.1f} ккал\n"

    messagebox.showinfo("История питания", history_text)

def clear_history():
    result = messagebox.askyesno(
        "Очистка истории",
        "Очистить историю за сегодня?",
        icon='question'
    )

    if result:
        deleted_count = db.clear_today_history()
        messagebox.showinfo("Очистка истории", f"Удалено записей за сегодня: {deleted_count}")

        global total_calories
        total_calories = 0
        calories_list.clear()
        products_list.clear()
        update_display()

#Интерфейс
root = tk.Tk()
root.title("Калькулятор калорий с базой данных")
root.geometry("500x600")

title_label = tk.Label(root, text="Калькулятор калорий", font=("Arial", 14, "bold"))
title_label.pack(pady=10)

#Рост, вес, возраст
frame1 = tk.Frame(root)
frame1.pack(pady=5)
tk.Label(frame1, text="Вес (кг)").grid(row=0, column=0)
tk.Label(frame1, text="Рост (см)").grid(row=0, column=1)
tk.Label(frame1, text="Возраст").grid(row=0, column=2)

weight_var = tk.StringVar()
weight_entry = tk.Entry(frame1, textvariable=weight_var, width=5)
weight_entry.grid(row=1, column=0)

height_var = tk.StringVar()
height_entry = tk.Entry(frame1, textvariable=height_var, width=5)
height_entry.grid(row=1, column=1)

age_var = tk.StringVar()
age_entry = tk.Entry(frame1, textvariable=age_var, width=5)
age_entry.grid(row=1, column=2)

#Пол, цель, активность
frame2 = tk.Frame(root)
frame2.pack(pady=5)

sex_var = tk.StringVar(value="Мужчина")
ttk.Combobox(frame2, textvariable=sex_var, values=["Мужчина", "Женщина"], width=10).grid(row=0, column=0, padx=5)

goal_var = tk.StringVar(value="Поддержание веса")
ttk.Combobox(frame2, textvariable=goal_var, values=["Поддержание веса", "Похудение", "Набор массы"], width=15).grid(
    row=0, column=1, padx=5)

activity_var = tk.StringVar(value="Средняя активность")
ttk.Combobox(frame2, textvariable=activity_var, values=[
    "Сидячий (офис)", "Низкая активность", "Средняя активность", "Высокая активность", "Очень высокая активность"],
             width=18).grid(row=0, column=2, padx=5)

calc_button = tk.Button(frame2, text="Рассчитать норму", command=calculate_bmr)
calc_button.grid(row=0, column=3, padx=5)

daily_label = tk.Label(root, text=f"Дневная норма калорий: {daily_calories:.0f} ккал", font=("Arial", 12))
daily_label.pack(pady=5)

#Статистика из бд
db_stats_label = tk.Label(root, text="📊 Сегодня съедено: 0 ккал", font=("Arial", 10), fg="blue")
db_stats_label.pack(pady=2)

#Продукты
product_var = tk.StringVar()
product_menu = ttk.Combobox(root, textvariable=product_var, width=30)
product_menu['values'] = sorted(list(products.keys()))
product_menu.pack(pady=5)
product_menu.set("Выберите продукт")

grams_var = tk.StringVar()
grams_entry = tk.Entry(root, textvariable=grams_var, width=30)
grams_entry.pack(pady=5)
grams_entry.insert(0, "Граммы")

add_button = tk.Button(root, text="Добавить продукт", command=add_product)
add_button.pack(pady=10)

#Фрейм для кнопок истории
history_frame = tk.Frame(root)
history_frame.pack(pady=5)

#Кнопка просмотра истории
history_button = tk.Button(history_frame, text="📋 Показать историю", command=show_db_history)
history_button.grid(row=0, column=0, padx=5)

#Кнопка очистки истории
clear_button = tk.Button(history_frame, text="🗑️ Очистить историю", command=clear_history, bg="#ffcccc")
clear_button.grid(row=0, column=1, padx=5)

result_label = tk.Label(root, text="Общая калорийность: 0 ккал", font=("Arial", 12))
result_label.pack(pady=5)

tracker_label = tk.Label(root, text="", font=("Arial", 10), justify="left")
tracker_label.pack(pady=5)

advice_label = tk.Label(root, text="", font=("Arial", 12, "italic"))
advice_label.pack(pady=5)

graph_button = tk.Button(root, text="Показать график калорий", command=show_graph)
graph_button.pack(pady=10)

root.mainloop()