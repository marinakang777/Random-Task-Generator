import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import json
import os
from datetime import datetime

# --- Configuration ---
HISTORY_FILE_PATH = "history.json"

# --- Data ---
# Предварительно заданные задачи с указанием типа (можно расширить)
# Формат: {"description": "Название задачи", "type": "Тип задачи"}
DEFAULT_TASKS = [
    {"description": "Прочитать статью по теме", "type": "Учёба"},
    {"description": "Сделать зарядку (15 минут)", "type": "Спорт"},
    {"description": "Проверить почту и ответить на важные письма", "type": "Работа"},
    {"description": "Написать план на следующий день", "type": "Работа"},
    {"description": "Изучить новую главу учебника", "type": "Учёба"},
    {"description": "Пробежка (30 минут)", "type": "Спорт"},
    {"description": "Позвонить другу/родственнику", "type": "Личное"},
    {"description": "Послушать образовательный подкаст", "type": "Учёба"},
    {"description": "Разработать новый компонент", "type": "Работа"},
    {"description": "Медитация (10 минут)", "type": "Спорт"},
]

tasks = [] # Здесь будут храниться все задачи (начальные + добавленные пользователем)
history = [] # Список для истории сгенерированных задач

# --- File Operations ---
def load_tasks():
    """Загружает задачи из файла, если он существует. Иначе использует предопределенные."""
    global tasks
    if os.path.exists(HISTORY_FILE_PATH):
        try:
            with open(HISTORY_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tasks = data.get("tasks", DEFAULT_TASKS)
                history = data.get("history", [])
        except (IOError, json.JSONDecodeError) as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные из {HISTORY_FILE_PATH}: {e}\nИспользуются задачи по умолчанию.")
            tasks = DEFAULT_TASKS
            history = []
    else:
        tasks = DEFAULT_TASKS
        history = []

def save_data():
    """Сохраняет текущий список задач и историю в JSON-файл."""
    try:
        with open(HISTORY_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump({"tasks": tasks, "history": history}, f, indent=4, ensure_ascii=False)
    except IOError as e:
        messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные в {HISTORY_FILE_PATH}: {e}")

# --- Core Logic ---
def add_task(description, task_type):
    """Добавляет новую задачу. Проверяет корректность ввода."""
    if not description.strip(): # Проверка на пустую строку
        messagebox.showwarning("Ошибка ввода", "Описание задачи не может быть пустым.")
        return False
    new_task = {"description": description.strip(), "type": task_type.strip() if task_type.strip() else "Без категории"}
    tasks.append(new_task)
    save_data()
    update_task_types_filter() # Обновить фильтры после добавления новой задачи
    return True

def generate_random_task(selected_type=None):
    """
    Выбирает случайную задачу.
    Если указан selected_type, фильтрует задачи по этому типу.
    """
    filtered_tasks = tasks
    if selected_type and selected_type != "Все типы":
        filtered_tasks = [task for task in tasks if task.get("type") == selected_type]

    if not filtered_tasks:
        return {"description": "Нет задач для данного фильтра", "type": "Информация"}

    chosen_task = random.choice(filtered_tasks)

    # Формируем запись в историю
    history_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task": chosen_task.get("description"),
        "type": chosen_task.get("type")
    }
    history.append(history_entry)
    save_data()
    update_history_display()
    return chosen_task

# --- GUI ---
class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("700x600")

        load_tasks() # Загружаем задачи и историю при запуске

        self.create_widgets()
        self.update_history_display()
        self.update_task_types_filter()

    def create_widgets(self):
        # --- Frames ---
        control_frame = ttk.LabelFrame(self.root, text="Управление", padding=(10, 5))
        control_frame.pack(pady=10, padx=10, fill="x")

        task_frame = ttk.LabelFrame(self.root, text="Сгенерированная задача", padding=(10, 5))
        task_frame.pack(pady=5, padx=10, fill="x")

        history_frame = ttk.LabelFrame(self.root, text="История задач", padding=(10, 5))
        history_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Control Frame Widgets ---
        # Filter
        ttk.Label(control_frame, text="Фильтр по типу:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.filter_type_var = tk.StringVar()
        self.filter_type_combo = ttk.Combobox(control_frame, textvariable=self.filter_type_var, state="readonly", width=20)
        self.filter_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type_combo.bind("<<ComboboxSelected>>", self.on_filter_change)

        # Add Task Button
        add_task_btn = ttk.Button(control_frame, text="Добавить задачу", command=self.open_add_task_dialog)
        add_task_btn.grid(row=0, column=2, padx=10, pady=5)

        # Generate Button
        self.generate_btn = ttk.Button(control_frame, text="Сгенерировать задачу", command=self.generate_and_display_task)
        self.generate_btn.grid(row=1, column=0, columnspan=3, pady=10)

        # --- Task Frame Widgets ---
        self.task_label = ttk.Label(task_frame, text="Нажмите кнопку для генерации задачи", wraplength=600, font=("Arial", 12))
        self.task_label.pack(pady=10)

        # --- History Frame Widgets ---
        self.history_tree_scroll = ttk.Scrollbar(history_frame)
        self.history_tree_scroll.pack(side="right", fill="y")
        self.history_tree_scroll_x = ttk.Scrollbar(history_frame, orient="horizontal")
        self.history_tree_scroll_x.pack(side="bottom", fill="x")

        columns = ("timestamp", "type", "task")
        self.history_table = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings",
            yscrollcommand=self.history_tree_scroll.set,
            xscrollcommand=self.history_tree_scroll_x.set
        )

        self.history_table.heading("timestamp", text="Время")
        self.history_table.heading("type", text="Тип")
        self.history_table.heading("task", text="Задача")

        self.history_table.column("timestamp", width=150, anchor="w")
        self.history_table.column("type", width=100, anchor="center")
        self.history_table.column("task", width=350, anchor="w")

        self.history_table.pack(fill="both", expand=True)
        self.history_tree_scroll.config(command=self.history_table.yview)
        self.history_tree_scroll_x.config(command=self.history_table.xview)

    def update_task_types_filter(self):
        """Обновляет список доступных типов задач для фильтрации."""
        unique_types = sorted(list(set(task.get("type", "Без категории") for task in tasks)))
        filter_options = ["Все типы"] + unique_types
        self.filter_type_combo['values'] = filter_options
        # Если текущий выбранный тип больше не существует, сбросить фильтр
        current_filter = self.filter_type_var.get()
        if current_filter not in filter_options:
            self.filter_type_var.set("Все типы")

    def on_filter_change(self, event=None):
        """Вызывается при изменении фильтра. Перегенерирует задачу, чтобы учесть фильтр."""
        self.generate_and_display_task()

    def generate_and_display_task(self):
        """Генерирует задачу и отображает ее в GUI."""
        selected_type = self.filter_type_var.get()
        task_task_data.get('type', 'Без типа')})")
        else:
            self.task_label.config(text="Ошибка генерации задачи.")

    def update_history_display(self):
        """Очищает и обновляет таблицу истории."""
        for item in self.history_table.get_children():
            self.history_table.delete(item)

        # Отображаем историю в обратном порядке (последние сверху)
        for entry in reversed(history):
            try:
                self.history_table.insert("", "end", values=(
                    entry.get("timestamp", "N/A"),
                    entry.get("type", "N/A"),
                    entry.get("task", "N/A")
                ))
            except Exception as e:
                print(f"Ошибка при добавлении в таблицу истории: {e}. Запись: {entry}") # Логирование для отладки

    def open_add_task_dialog(self):
        """Открывает диалоговое окно для добавления новой задачи."""
        # Можно использовать simpledialog, но для двух полей (описание и тип) лучше сделать свой Toplevel окно.

        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить новую задачу")
        dialog.geometry("350x200")
        dialog.transient(self.root) # Делает окно модальным относительно главного
        dialog.grab_set() # Блокируем взаимодействие с главным окном

        dialog_frame = ttk.Frame(dialog, padding=(10, 10))
        dialog_frame.pack(fill="both", expand=True)

        ttk.Label(dialog_frame, text="Описание задачи:").grid(row=0, column=0, sticky="w", pady=5)
        desc_entry = ttk.Entry(dialog_frame, width=30)
        desc_entry.grid(row=0, column=1, pady=5)
        desc_entry.focus_set() # Устанавливаем фокус на поле ввода

        ttk.Label(dialog_frame, text="Тип задачи (учёба, спорт, работа, личное):").grid(row=1, column=0, sticky="w", pady=5)
        type_entry = ttk.Entry(dialog_frame, width=30)
        type_entry.grid(row=1, column=1, pady=5)

        def save_and_close():
            description = desc_entry.get()
            task_type = type_entry.get()
            if add_task(description, task_type):
                dialog.destroy() # Закрываем диалог только если задача успешно добавлена

        add_button = ttk.Button(dialog_frame, text="Добавить", command=save_and_close)
        add_button.grid(row=2, column=0, columnspan=2, pady=15)

        # Обработка нажатия Enter в полях ввода
        desc_entry.bind("<Return>", lambda event: save_and_close())
        type_entry.bind("<Return>", lambda event: save_and_close())


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGeneratorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (save_data(), root.destroy())) # Безопасное закрытие
    root.mainloop()
