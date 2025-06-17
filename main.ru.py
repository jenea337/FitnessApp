import customtkinter as ctk
import json
from datetime import datetime

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
app=ctk.CTk()
app.title("Fitness Project")
app.geometry("900x800")
user_data = {}

def save_user_input(gender, weight, height, body_type,age, support=None, activity=None):
    user_data["gender"] = gender
    user_data["weight"] = weight
    user_data["height"] = height
    user_data["body_type"] = body_type
    user_data["support"] = support
    user_data["activity"] = activity
    user_data["age"] = age

    # Очистим старые элементы с экрана
    for widget in app.winfo_children():
        widget.destroy()


    show_result_screen()


def calculate_kbju(data):
    gender = data["gender"]
    weight = float(data["weight"])
    height = float(data["height"])
    body_type = data["body_type"]
    activity = data.get("activity")
    goal = data["goal"]
    age = float(data["age"])

    activity_factor = 1.2
    if goal == "Рельеф":
        if activity == "Каждый день":
            activity_factor = 1.6
        elif activity == "3–4 раза в неделю":
            activity_factor = 1.4
        elif activity == "1–2 раза в неделю":
            activity_factor = 1.2

    if gender == "Мужчина":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # поправка на тип тела
    if body_type == "Широкая кость":
        bmr *= 1.1
    elif body_type == "Худощавый (узкая кость)":
        bmr *= 0.9

    calories = bmr * activity_factor

    if goal == "Похудение":
        calories -= 300
    elif goal == "Рельеф":
        pass
    elif goal == "Поддержание формы":
        calories = bmr * 1.4

    protein = weight * 2  # г на 1 кг массы
    fat = weight * 1  # г на 1 кг массы
    carbs = (calories - (protein * 4 + fat * 9)) / 4  # остаток на углеводы

    return round(calories), round(protein), round(fat), round(carbs)



def show_result_screen():
    goal = user_data.get("goal")
    # Расчёт КБЖУ
    calories, protein, fat, carbs = calculate_kbju(user_data)


    kkal_info = ctk.CTkLabel(
        app,
        text=f"Ваша норма КБЖУ:\nКалории: {calories} ккал\nБелки: {protein} г\nЖиры: {fat} г\nУглеводы: {carbs} г"
    )
    kkal_info.pack(pady=10)



    title = ctk.CTkLabel(app, text="Результаты", font=ctk.CTkFont(size=18, weight="bold"))
    title.pack(pady=10)





    if goal == "Рельеф":
        recommend = ctk.CTkLabel(app, text="💡 Советы: Увеличивай нагрузку, когда станет легко")
        recommend.pack(pady=5)

        video = ctk.CTkLabel(
            app,
            text="🔗 Видео: https://www.youtube.com/results?search_query=рельеф+тренировки",
            text_color="blue",
            cursor="hand2"
        )
        video.pack(pady=5)

        def open_video(event):
            import webbrowser
            webbrowser.open("https://www.youtube.com/results?search_query=рельеф+тренировки")

        video.bind("<Button-1>", open_video)

    elif goal == "Поддержание формы" and user_data.get("support") == "Питание и тренировки":
        support_recommend = ctk.CTkLabel(app, text="🏃‍♂️ Совет: Начни бегать, отжиматься и подтягиваться ежедневно")
        support_recommend.pack(pady=5)

    elif goal == "Похудение":
        note = ctk.CTkLabel(app, text="📉 Просто следуй КБЖУ и отслеживай питание в течение месяца")
        note.pack(pady=5)

    # ——— Трекер питания на день ———

    entry_frame = ctk.CTkFrame(app)
    entry_frame.pack(pady=10)

    food_name = ctk.CTkEntry(entry_frame, placeholder_text="Продукт")
    food_name.grid(row=0, column=0, padx=5)

    cal_entry = ctk.CTkEntry(entry_frame, placeholder_text="Ккал")
    cal_entry.grid(row=0, column=1, padx=5)

    protein_entry = ctk.CTkEntry(entry_frame, placeholder_text="Б")
    protein_entry.grid(row=0, column=2, padx=5)

    fat_entry = ctk.CTkEntry(entry_frame, placeholder_text="Ж")
    fat_entry.grid(row=0, column=3, padx=5)

    carb_entry = ctk.CTkEntry(entry_frame, placeholder_text="У")
    carb_entry.grid(row=0, column=4, padx=5)

    daily_log = []

    def save_log():
        total_cals = sum(item["calories"] for item in daily_log)
        total_p = sum(item["protein"] for item in daily_log)
        total_f = sum(item["fat"] for item in daily_log)
        total_c = sum(item["carbs"] for item in daily_log)

        log_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "goal": goal,
            "products": daily_log,
            "total": {
                "calories": total_cals,
                "protein": total_p,
                "fat": total_f,
                "carbs": total_c
            }
        }

        try:
            with open("daily_log.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
            print("Дневник сохранён!")
        except Exception as e:
            print("Ошибка при сохранении:", e)


    total_label = ctk.CTkLabel(app, text="Сумма за день:\nКкал: 0 | Б: 0 | Ж: 0 | У: 0")
    total_label.pack(pady=10)

    def update_summary():
        total_cals = sum(item["calories"] for item in daily_log)
        total_p = sum(item["protein"] for item in daily_log)
        total_f = sum(item["fat"] for item in daily_log)
        total_c = sum(item["carbs"] for item in daily_log)

        status = []
        if total_cals < calories:
            status.append("Ккал: недостаточно")
        elif total_cals > calories:
            status.append("Ккал: перебор")
        else:
            status.append("Ккал: ок")

        total_label.configure(
            text=f"Сумма за день:\nКкал: {total_cals} | Б: {total_p} | Ж: {total_f} | У: {total_c}\n" +
                 " | ".join(status)
        )

    def add_food():
        try:
            item = {
                "name": food_name.get(),
                "calories": int(cal_entry.get()),
                "protein": int(protein_entry.get()),
                "fat": int(fat_entry.get()),
                "carbs": int(carb_entry.get())
            }
            daily_log.append(item)
            update_summary()

            
            food_name.delete(0, "end")
            cal_entry.delete(0, "end")
            protein_entry.delete(0, "end")
            fat_entry.delete(0, "end")
            carb_entry.delete(0, "end")
        except ValueError:
            print("Ошибка: введите числовые значения для КБЖУ")

    def check_kbju():
        total_cals = sum(item["calories"] for item in daily_log)
        total_p = sum(item["protein"] for item in daily_log)
        total_f = sum(item["fat"] for item in daily_log)
        total_c = sum(item["carbs"] for item in daily_log)

        messages = []

        def compare(actual, target, name):
            if actual < target * 0.9:
                return f"{name}:  Недостаток"
            elif actual > target * 1.1:
                return f"{name}:  Перебор"
            else:
                return f"{name}:  В пределах нормы"

        messages.append(compare(total_cals, calories, "Ккал"))
        messages.append(compare(total_p, protein, "Белки"))
        messages.append(compare(total_f, fat, "Жиры"))
        messages.append(compare(total_c, carbs, "Углеводы"))

        result = "\n".join(messages)

        result_window = ctk.CTkToplevel(app)
        result_window.title("Результат дня")
        result_window.geometry("300x200")

        msg = ctk.CTkLabel(result_window, text=result, font=ctk.CTkFont(size=14))
        msg.pack(pady=20)


    def show_history():
        try:
            with open("daily_log.json", "r", encoding="utf-8") as f:
                logs = [json.loads(line.strip()) for line in f.readlines()]
        except FileNotFoundError:
            logs = []

        history_window = ctk.CTkToplevel(app)
        history_window.title("История")
        history_window.geometry("400x300")

        if not logs:
            no_data = ctk.CTkLabel(history_window, text="Нет сохранённых данных.", font=ctk.CTkFont(size=14))
            no_data.pack(pady=20)
            return

        for entry in logs[-10:]: 
            date = entry["date"]
            total = entry["total"]
            line = f"{date} | К: {total['calories']} Б: {total['protein']} Ж: {total['fat']} У: {total['carbs']}"
            label = ctk.CTkLabel(history_window, text=line, anchor="w")
            label.pack(anchor="w", padx=10)


    if goal in ["Рельеф", "Поддержание"]:
        show_tips_and_links(goal)

    add_button = ctk.CTkButton(app, text="Добавить в дневник", command=add_food)
    add_button.pack()
    save_button = ctk.CTkButton(app, text="Сохранить день", command=save_log)
    save_button.pack(pady=5)
    check_button = ctk.CTkButton(app, text="Проверить результат", command=check_kbju)
    check_button.pack(pady=5)
    history_button = ctk.CTkButton(app, text="Показать историю", command=show_history)
    history_button.pack(pady=5)

def show_tips_and_links(goal):
    tips_window = ctk.CTkToplevel(app)
    tips_window.title("Советы и Видео")
    tips_window.geometry("400x300")
    if goal == "Рельеф":
        tips_text = (
            "Советы для рельефа:\n"
            "- Удваивай тренировки, когда становится легко\n"
            "- Не забывай про восстановление\n\n"
            "Видео:\n"
            "https://www.youtube.com/watch?v=example1\n"
            "https://www.youtube.com/watch?v=example2"
        )
    elif goal == "Поддержание":
        tips_text = (
            "Советы для поддержания формы:\n"
            "- Начни бегать по утрам\n"
            "- Подтягивайся и отжимайся\n"
            "- Старайся быть активным каждый день"
        )
    else:
        tips_text = "Советов для этой цели нет."
    label = ctk.CTkLabel(tips_window, text=tips_text, justify="left", font=ctk.CTkFont(size=14))
    label.pack(padx=20, pady=20)




def show_input_fields(goal):

    input_label = ctk.CTkLabel(app, text="Введите свои данные:", font=ctk.CTkFont(size=16, weight="bold"))
    input_label.pack(pady=10)

    
    gender_label = ctk.CTkLabel(app, text="Пол:")
    gender_label.pack()
    gender_option = ctk.CTkOptionMenu(app, values=["Мужской", "Женский"])
    gender_option.pack(pady=5)

    
    weight_label = ctk.CTkLabel(app, text="Вес (кг):")
    weight_label.pack()
    weight_entry = ctk.CTkEntry(app)
    weight_entry.pack(pady=5)

    
    height_label = ctk.CTkLabel(app, text="Рост (см):")
    height_label.pack()
    height_entry = ctk.CTkEntry(app)
    height_entry.pack(pady=5)

    
    body_type_label = ctk.CTkLabel(app, text="Тип тела:")
    body_type_label.pack()
    body_type_option = ctk.CTkOptionMenu(app, values=["Худощавый (узкая кость)", "Широкая кость"])
    body_type_option.pack(pady=5)

    
    age_label = ctk.CTkLabel(app, text="Возраст:", font=ctk.CTkFont(size=14))
    age_label.pack(pady=(10, 2))
    age_entry = ctk.CTkEntry(app)
    age_entry.pack(pady=(0, 10))


    if goal == "Рельеф":
        activity_label = ctk.CTkLabel(app, text="Активность:")
        activity_label.pack()
        activity_option = ctk.CTkOptionMenu(app, values=["Каждый день", "3–4 раза в неделю", "1–2 раза в неделю"])
        activity_option.pack(pady=5)

    elif goal == "Поддержание":
        support_label = ctk.CTkLabel(app, text="Выберите режим:")
        support_label.pack()
        support_option = ctk.CTkOptionMenu(app, values=["Только питание", "Питание и тренировки"])
        support_option.pack(pady=5)



    
    continue_button = ctk.CTkButton(app, text="Продолжить", command=lambda: save_user_input(
        gender_option.get(),
        weight_entry.get(),
        height_entry.get(),
        body_type_option.get(),
        age_entry.get(),
        support_option.get() if goal == "Поддержание формы" else None,
        activity_option.get() if goal == "Рельеф" else None
    ))
    continue_button.pack(pady=15)






def select_goal(goal):
    
        label.pack_forget()
        button1.pack_forget()
        button2.pack_forget()
        button3.pack_forget()

   
        user_data["goal"] = goal


        show_input_fields(goal)
        result_label = ctk.CTkLabel(app, text=f"Вы выбрали: {goal}", font=ctk.CTkFont(size=18, weight="bold"))
        result_label.pack(pady=20)





label = ctk.CTkLabel(app, text="Выберите свою цель", font=ctk.CTkFont(size=18, weight="bold"))
label.pack(pady=20)


button1 = ctk.CTkButton(app, text="Похудение", command=lambda: select_goal("Похудение"))
button1.pack(pady=10)

button2 = ctk.CTkButton(app, text="Рельеф", command=lambda: select_goal("Рельеф"))
button2.pack(pady=10)

button3 = ctk.CTkButton(app, text="Поддержание формы", command=lambda: select_goal("Поддержание"))
button3.pack(pady=10)



app.mainloop()