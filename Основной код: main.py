import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import json
import os
from datetime import datetime

# --- Configuration ---
HISTORY_FILE_PATH = "history.json"

# --- Data ---
DEFAULT_TASKS = [
    {"description": "Прочитать главу учебника по программированию", "type": "Учёба"},
    {"description": "Сделать 15-минутную зарядку", "type": "Спорт"},
    {"description": "Проверить рабочую почту и ответить на важные письма", "type": "Работа"},
    {"description": "Составить список дел на завтра", "type": "Работа"},
    {"description": "Изучить новую концепцию из курса", "type": "Учёба"},
    {"description": "Краткая пробежка (30 минут)", "type": "Спорт"},
    {"description": "Позвонить члену семьи или другу", "type": "Личное"},
    {"description": "Прослушать образовательный подкаст", "type": "Учёба"},
    {"description": "Разработать новый UI-компонент", "type": "Работа"},
    {"description": "Сеанс медитации (10 минут)", "type": "Спорт"},
]

# Глобальные переменные
tasks = []
history = []

# --- File Operations ---
def load_tasks():
    """Загружает задачи и историю из файла. Инициализирует переменные."""
    global tasks, history # !!! ИСПРАВЛЕНО: Явное объявление глобальных переменных
    if os.path.exists(HISTORY_FILE_PATH):
        try:
            with open(HISTORY_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Если в файле нет ключей, используем значения по умолчанию
                tasks = data.get("tasks", DEFAULT_TASKS)
                history = data.get("history", [])
        except (IOError, json.JSONDecodeError) as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные из {HISTORY_FILE_PATH}: {e}\nИспользуются задачи по умолчанию, история будет пустой.")
            tasks = DEFAULT_TASKS # Сбрасываем на дефолтные в случае ошибки
            history = []
    else:
        # Если файл не существует, инициализируем значениями по умолчанию
        tasks = DEFAULT_TASKS
        history = []
    # Убедимся, что history - это список, если вдруг в файле было что-то некорректное
    if not isinstance(history, list):
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
    """Добавляет новую задачу с валидацией описания и типа."""
    # !!! ИСПРАВЛЕНО: Добавлена валидация типа задачи
    if not description.strip():
        messagebox.showwarning("Ошибка ввода", "Описание задачи не может быть пустым.")
        return False
    if not task_type.strip():
        messagebox.showwarning("Ошибка ввода", "Тип задачи не может быть пустым.")
        return False

    new_task = {"description": description.strip(), "type": task_type.strip()}
    tasks.append(new_task)
    save_data()
    return True

def generate_random_task(selected_type=None):
    """
    Выбирает случайную задачу.
    Если указан selected_type, фильтрует задачи по этому типу.
    Записывает выбранную задачу в историю.
    """
    filtered_tasks = tasks
    # !!! ИСПРАВЛЕНО: Фильтрация по типу задачи
    if selected_type and selected_type != "Все типы":
        filtered_tasks = [task for task in tasks if task.get("type") == selected_type]

    if not filtered_tasks:
        return {"description": "Нет задач для выбранного фильтра.", "type": "Информация"}

    chosen_task = random.choice(filtered_tasks)

    # Запись в историю
    history_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task": chosen_task.get("description"),
        "type": chosen_task.get("type")
    }
    history.append(history_entry)
    save_data() # !!! ИСПРАВЛЕНО: сохраняем данные после добавления в историю
    return chosen_task

# --- GUI ---
class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор Случайных Задач")
        self.root.geometry("750x600")

        load_tasks() # Загружаем задачи и историю при старте

        self.create_widgets()
        self.update_history_display()
        self.update_task_types_filter()

    def create_widgets(self):
        # --- Frames ---
        control_frame = ttk.LabelFrame(self.root, text="Панель управления", padding=(10, 5))
        control_frame.pack(pady=10, padx=10, fill="x")

        task_frame = ttk.LabelFrame(self.root, text="Сгенерированная задача", padding=(10, 5))
        task_frame.pack(pady=5, padx=10, fill="x")

        history_frame = ttk.LabelFrame(self.root, text="История выполненных задач", padding=(10, 5))
        history_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Control Frame Widgets ---
        ttk.Label(control_frame, text="Фильтр по типу:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.filter_type_var = tk.StringVar()
        self.filter_type_combo = ttk.Combobox(control_frame, textvariable=self.filter_type_var, state="readonly", width=25)
        self.filter_type_combo.grid(row=0, column=1, padx=5, pady=5)

        # Привязываем событие изменения фильтра к обновлению отображения задачи
        self.filter_type_combo.bind("<<ComboboxSelected>>", self.on_filter_change)

        add_task_btn = ttk.Button(control_frame, text="Добавить задачу", command=self.open_add_task_dialog)
        add_task_btn.grid(row=0, column=2, padx=10, pady=5)

        # !!! ИСПРАВЛЕНО: Кнопка генерации теперь является отдельным элементом
        self.generate_btn = ttk.Button(control_frame, text="Сгенерировать задачу", command=self.generate_and_display_task)
        self.generate_btn.grid(row=0, column=3, padx=5, pady=5)

        # --- Task Frame Widgets ---
        self.task_description_label = ttk.Label(task_frame, text="Задача: ", font=("TkDefaultFont", 12, "bold"), wraplength=600)
        self.task_description_label.pack(pady=10)
        self.task_type_label = ttk.Label(task_frame, text="Тип: ", font=("TkDefaultFont", 10, "italic"))
        self.task_type_label.pack(pady=5)

        # --- History Frame Widgets ---
        self.history_tree = ttk.Treeview(history_frame, columns=("Timestamp", "Type", "Description"), show="headings")
        self.history_tree.heading("Timestamp", text="Дата и время")
        self.history_tree.heading("Type", text="Тип")
        self.history_tree.heading("Description", text="Описание")

        # Настройка ширины колонок
        self.history_tree.column("Timestamp", width=180, anchor=tk.W)
        self.history_tree.column("Type", width=100, anchor=tk.W)
        self.history_tree.column("Description", width=400, anchor=tk.W)

        # Скруллбары для Treeview
        vsb = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        vsb.pack(side=tk.RIGHT, fill="y")
        hsb = ttk.Scrollbar(history_frame, orient="horizontal", command=self.history_tree.xview)
        hsb.pack(side=tk.BOTTOM, fill="x")
        self.history_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.history_tree.pack(fill="both", expand=True)

        # Изначальное отображение задачи (если есть)
        self.display_initial_task()

    def display_initial_task(self):
        """Отображает первую задачу при запуске, если она есть."""
        if tasks:
            # Показываем любую задачу, для демонстрации
            initial_task = tasks[0]
            self.task_description_label.config(text=f"Задача: {initial_task.get('description', 'N/A')}")
            self.task_type_label.config(text=f"Тип: {initial_task.get('type', 'N/A')}")
            self.filter_type_var.set("Все типы") # Сбрасываем фильтр
        else:
            self.task_description_label.config(text="Задача: Нет доступных задач!")
            self.task_type_label.config(text="")

    def generate_and_display_task(self):
        """
        !!! ИСПРАВЛЕНО: Корректно генерирует и отображает задачу.
        Вызывает generate_random_task с учетом выбранного фильтра.
        Обновляет метки с описанием и типом задачи.
        """
        selected_filter = self.filter_type_var.get()
        generated_task = generate_random_task(selected_filter if selected_filter else None)

        self.task_description_label.config(text=f"Задача: {generated_task.get('description', 'N/A')}")
        self.task_type_label.config(text=f"Тип: {generated_task.get('type', 'N/A')}")

        self.update_history_display() # Обновляем историю после генерации

    def on_filter_change(self, event=None):
        """Обработчик изменения фильтра, который запускает генерацию задачи."""
        # При изменении фильтра, сразу генерируем новую задачу, чтобы она соответствовала фильтру
        self.generate_and_display_task()

    def update_task_types_filter(self):
        """Обновляет список типов задач в выпадающем меню фильтра."""
        # Собираем уникальные типы из существующих задач
        # Добавляем "Все типы" как первый вариант
        unique_types = sorted(list(set(task.get("type") for task in tasks)))
        filter_options = ["Все типы"] + unique_types
        self.filter_type_combo['values'] = filter_options
        # Устанавливаем "Все типы" по умолчанию, если комбобокс еще не заполнен
        if not self.filter_type_var.get() or self.filter_type_var.get() not in filter_options:
            self.filter_type_var.set("Все типы")

    def update_history_display(self):
        """Очищает и заполняет Treeview данными из глобальной истории."""
        # Очищаем старые данные
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Заполняем новыми данными (от новых к старым)
        for entry in reversed(history):
            self.history_tree.insert("", tk.END, values=(
                entry.get("timestamp", "N/A"),
                entry.get("type", "N/A"),
                entry.get("task", "N/A")
            ))

    def open_add_task_dialog(self):
        """Открывает диалоговое окно для добавления новой задачи."""
        dialog = AddTaskDialog(self.root)
        if dialog.result:
            description, task_type = dialog.result
            if add_task(description, task_type):
                # Если задача успешно добавлена, обновляем фильтр типов
                self.update_task_types_filter()
                # Перевыбираем "Все типы" в фильтре
                self.filter_type_var.set("Все типы")
                messagebox.showinfo("Успех", "Задача успешно добавлена!")
            else:
                # Ошибка валидации уже показана в add_task
                pass

class AddTaskDialog(simpledialog.Dialog):
    """Пользовательское диалоговое окно для добавления задачи."""
    def body(self, master):
        ttk.Label(master, text="Описание задачи:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.description_entry = ttk.Entry(master, width=40)
        self.description_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(master, text="Тип задачи (например, Работа, Учёба, Спорт):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.type_entry = ttk.Entry(master, width=40)
        self.type_entry.grid(row=1, column=1, padx=5, pady=2)

        return self.description_entry # Устанавливаем фокус на первое поле

    def apply(self):
        description = self.description_entry.get()
        task_type = self.type_entry.get()
        # !!! ИСПРАВЛЕНО: В `add_task` уже есть валидация. Здесь просто передаем данные.
        self.result = (description, task_type)


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGeneratorApp(root)
    root.mainloop()

