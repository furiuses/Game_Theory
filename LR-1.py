import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import random
from datetime import datetime


# ---------------------------
# Функции общего назначения
# ---------------------------
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------
# Вкладка для одноматричных игр
# ---------------------------
class MatrixGameFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.rows = tk.IntVar(value=2)
        self.cols = tk.IntVar(value=2)
        self.matrix_entries = []
        self.output_dest = tk.StringVar(value="results")  # "results" или "file"
        self.create_widgets()

    def create_widgets(self):
        # Верхняя панель с настройками
        top_frame = tk.Frame(self)
        top_frame.pack(padx=5, pady=5, fill=tk.X)

        # Размерность матрицы
        dim_frame = tk.LabelFrame(top_frame, text="Размерность матрицы", padx=5, pady=5)
        dim_frame.pack(side=tk.LEFT, padx=5)

        vcmd = (self.register(self.validate_spinbox), '%P')

        tk.Label(dim_frame, text="Rows:").grid(row=0, column=0, padx=2, pady=2)
        tk.Spinbox(dim_frame, from_=1, to=50, textvariable=self.rows, width=5,
                   validate="key", validatecommand=vcmd,
                   command=self.update_matrix_input).grid(row=0, column=1, padx=2, pady=2)
        tk.Label(dim_frame, text="Columns:").grid(row=0, column=2, padx=2, pady=2)
        tk.Spinbox(dim_frame, from_=1, to=50, textvariable=self.cols, width=5,
                   validate="key", validatecommand=vcmd,
                   command=self.update_matrix_input).grid(row=0, column=3, padx=2, pady=2)
        tk.Button(dim_frame, text="Обновить матрицу", command=self.update_matrix_input) \
            .grid(row=0, column=4, padx=5, pady=2)

        # Панель кнопок операций
        op_frame = tk.Frame(top_frame)
        op_frame.pack(side=tk.LEFT, padx=5)
        tk.Button(op_frame, text="Загрузить из файла", command=self.load_from_file).pack(side=tk.LEFT, padx=2)
        tk.Button(op_frame, text="Сохранить в файл", command=self.save_matrix_to_file).pack(side=tk.LEFT, padx=2)
        tk.Button(op_frame, text="Случайная матрица", command=self.generate_random_matrix).pack(side=tk.LEFT, padx=2)
        tk.Button(op_frame, text="Maximin/Minimax", command=self.find_maximin_minimax).pack(side=tk.LEFT, padx=2)

        # Выбор места вывода
        output_frame = tk.Frame(self)
        output_frame.pack(padx=5, pady=5, fill=tk.X)
        tk.Label(output_frame, text="Output:").pack(side=tk.LEFT)
        tk.Radiobutton(output_frame, text="Results", variable=self.output_dest, value="results") \
            .pack(side=tk.LEFT)
        tk.Radiobutton(output_frame, text="File", variable=self.output_dest, value="file") \
            .pack(side=tk.LEFT)

        # Панель для удаления доминируемых стратегий
        dom_frame = tk.LabelFrame(self, text="Удаление доминируемых стратегий", padx=5, pady=5)
        dom_frame.pack(padx=5, pady=5, fill=tk.X)
        # Добавляем выбор: строки или столбцы
        self.player_choice = tk.StringVar(value="row")
        tk.Label(dom_frame, text="Стратегия:").pack(side=tk.LEFT, padx=2)
        tk.OptionMenu(dom_frame, self.player_choice, "row", "column").pack(side=tk.LEFT, padx=2)
        tk.Button(dom_frame, text="Удалить строго доминируемые", command=self.remove_strictly_dominated) \
            .pack(side=tk.LEFT, padx=5)
        tk.Button(dom_frame, text="Удалить слабо доминируемые", command=self.remove_weakly_dominated) \
            .pack(side=tk.LEFT, padx=5)

        # Панель ввода матрицы
        self.matrix_input_frame = tk.LabelFrame(self, text="Payoff Matrix", padx=5, pady=5)
        self.matrix_input_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.update_matrix_input()

        # Текст для вывода результатов
        self.result_text = tk.Text(self, height=10, wrap=tk.WORD)
        self.result_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def validate_spinbox(self, value_if_allowed):
        # Разрешаем пустую строку (пока пользователь не ввёл число)
        if value_if_allowed == "":
            return True
        try:
            val = int(value_if_allowed)
            return 1 <= val <= 100
        except ValueError:
            return False

    def update_matrix_input(self):
        for widget in self.matrix_input_frame.winfo_children():
            widget.destroy()
        self.matrix_entries = []
        rows = self.rows.get()
        cols = self.cols.get()
        if rows == 1 and cols == 1:
            messagebox.showerror("Ошибка",
                                 "Матрица не может быть размером 1x1!\nДопустимые размеры: 1x2, 2x1, или квадратные матрицы NxN.")
            self.cols.set(2)
            cols = 2
        # Заголовки столбцов
        for j in range(cols):
            tk.Label(self.matrix_input_frame, text=f"Col {j + 1}").grid(row=0, column=j + 1, padx=2, pady=2)
        # Поля ввода
        for i in range(rows):
            tk.Label(self.matrix_input_frame, text=f"Row {i + 1}").grid(row=i + 1, column=0, padx=2, pady=2)
            row_entries = []
            for j in range(cols):
                entry = tk.Entry(self.matrix_input_frame, width=8)
                entry.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                entry.insert(0, "0")
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)

    def get_matrix_from_input(self):
        rows = self.rows.get()
        cols = self.cols.get()
        if rows == 1 and cols == 1:
            messagebox.showerror("Ошибка", "Недопустимая размерность матрицы. Допустимые размеры: 1x2, 2x1 или NxN, где N >= 2")
            return None
        matrix = []
        try:
            for i in range(rows):
                row = []
                for j in range(cols):
                    row.append(float(self.matrix_entries[i][j].get()))
                matrix.append(row)
            return np.array(matrix)
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите числа во все ячейки матрицы")
            return None

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'r') as file:
                lines = [line.strip() for line in file if line.strip()]
            if not lines:
                messagebox.showerror("Ошибка", "Файл пуст!\n")
                return

            # Парсинг размеров матрицы
            try:
                dims = list(map(int, lines[0].split()))
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат размеров матрицы в файле!")
                return
            if len(dims) != 2:
                messagebox.showerror("Ошибка",
                                     "Первая строка должна содержать ровно два числа (количество строк и столбцов)!")
                return
            rows, cols = dims
            if rows == 1 and cols == 1:
                messagebox.showerror("Ошибка",
                                     "Матрица из файла не может быть размером 1x1!\nДопустимые размеры: 1x2, 2x1 или NxN.")
                return
            if rows < 1 or cols < 1:
                messagebox.showerror("Ошибка", "Размеры матрицы должны быть положительными!")
                return
            if rows > 20 or cols > 20:
                messagebox.showerror("Ошибка", "Максимальная размерность матрицы - 20x20!")
                return

            if len(lines) < 1 + rows:
                messagebox.showerror("Ошибка", "Недостаточно строк с данными в файле!")
                return

            matrix = []
            for i in range(1, 1 + rows):
                try:
                    vals = list(map(float, lines[i].split()))
                except ValueError:
                    messagebox.showerror("Ошибка", f"Некорректный ввод данных в строке {i + 1} (ожидались числа)!")
                    return
                if len(vals) != cols:
                    messagebox.showerror("Ошибка", f"В строке {i + 1} должно быть {cols} чисел, найдено {len(vals)}!")
                    return
                matrix.append(vals)

            self.rows.set(rows)
            self.cols.set(cols)
            self.update_matrix_input()
            for i in range(rows):
                for j in range(cols):
                    self.matrix_entries[i][j].delete(0, tk.END)
                    self.matrix_entries[i][j].insert(0, str(matrix[i][j]))
            self.output_result(f"Матрица успешно загружена из файла {file_path}\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {str(e)}")

    def save_matrix_to_file(self):
        matrix = self.get_matrix_from_input()
        if matrix is None:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'w') as file:
                file.write(f"{self.rows.get()} {self.cols.get()}\n")
                for row in matrix:
                    file.write(" ".join(map(str, row)) + "\n")
            self.output_result(f"Матрица сохранена в {file_path}\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")

    def generate_random_matrix(self):
        rows = self.rows.get()
        cols = self.cols.get()
        for i in range(rows):
            for j in range(cols):
                self.matrix_entries[i][j].delete(0, tk.END)
                self.matrix_entries[i][j].insert(0, str(random.randint(-10, 10)))
        self.output_result(f"Сгенерирована случайная матрица {rows}x{cols}\n")

    def find_maximin_minimax(self):
        matrix = self.get_matrix_from_input()
        if matrix is None:
            return
        try:
            # Для игрока по строкам
            row_minima = np.min(matrix, axis=1)
            maximin = np.max(row_minima)
            maximin_row = np.argmax(row_minima)
            # Для игрока по столбцам
            col_maxima = np.max(matrix, axis=0)
            minimax = np.min(col_maxima)
            minimax_col = np.argmin(col_maxima)
            saddle = (maximin == minimax)
            result = (f"Maximin (строковый игрок): Row {maximin_row + 1} со значением {maximin}\n"
                      f"Minimax (столбцовый игрок): Column {minimax_col + 1} со значением {minimax}\n"
                      f"{'Седловая точка существует' if saddle else 'Седловой точки нет'}\n")
            self.output_result(result)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при расчётах: {str(e)}")

    def remove_strictly_dominated(self):
        matrix = self.get_matrix_from_input()
        if matrix is None:
            return
        result = ""
        player = self.player_choice.get()
        if player == "row":
            rows_to_remove = set()
            info = []
            for i in range(matrix.shape[0]):
                for k in range(matrix.shape[0]):
                    if i != k and np.all(matrix[i, :] < matrix[k, :]):
                        rows_to_remove.add(i)
                        info.append(f"Строка {i + 1} строго доминируется строкой {k + 1}")
                        info.append(f"Удалена строка {i + 1}")
            if rows_to_remove:
                new_matrix = np.delete(matrix, list(rows_to_remove), axis=0)
                self.rows.set(new_matrix.shape[0])
                self.update_matrix_input()
                for i in range(new_matrix.shape[0]):
                    for j in range(new_matrix.shape[1]):
                        self.matrix_entries[i][j].delete(0, tk.END)
                        self.matrix_entries[i][j].insert(0, str(new_matrix[i, j]))
                result += "--- Удаление строго доминируемых строк ---\n" + "\n".join(info) + "\n"
                result += f"Удалено {len(rows_to_remove)} строк\nНовая матрица:\n{new_matrix}\n"
            else:
                result += "Строго доминируемых строк не найдено\n"
        else:  # player == "column"
            cols_to_remove = set()
            info = []
            for j in range(matrix.shape[1]):
                for l in range(matrix.shape[1]):
                    if j != l and np.all(matrix[:, j] < matrix[:, l]):
                        cols_to_remove.add(j)
                        info.append(f"Столбец {j + 1} строго доминируется столбцом {l + 1}")
                        info.append(f"Удален столбец {j + 1}")
            if cols_to_remove:
                new_matrix = np.delete(matrix, list(cols_to_remove), axis=1)
                self.cols.set(new_matrix.shape[1])
                self.update_matrix_input()
                for i in range(new_matrix.shape[0]):
                    for j in range(new_matrix.shape[1]):
                        self.matrix_entries[i][j].delete(0, tk.END)
                        self.matrix_entries[i][j].insert(0, str(new_matrix[i, j]))
                result += "--- Удаление строго доминируемых столбцов ---\n" + "\n".join(info) + "\n"
                result += f"Удалено {len(cols_to_remove)} столбцов\nНовая матрица:\n{new_matrix}\n"
            else:
                result += "Строго доминируемых столбцов не найдено\n"
        self.output_result(result)

    def remove_weakly_dominated(self):
        matrix = self.get_matrix_from_input()
        if matrix is None:
            return
        result = ""
        player = self.player_choice.get()
        if player == "row":
            rows_to_remove = set()
            info = []
            for i in range(matrix.shape[0]):
                for k in range(matrix.shape[0]):
                    if i != k and (np.all(matrix[i, :] <= matrix[k, :]) and np.any(matrix[i, :] < matrix[k, :])):
                        rows_to_remove.add(i)
                        info.append(f"Строка {i + 1} слабо доминируется строкой {k + 1}")
                        info.append(f"Удалена строка {i + 1}")
            if rows_to_remove:
                new_matrix = np.delete(matrix, list(rows_to_remove), axis=0)
                self.rows.set(new_matrix.shape[0])
                self.update_matrix_input()
                for i in range(new_matrix.shape[0]):
                    for j in range(new_matrix.shape[1]):
                        self.matrix_entries[i][j].delete(0, tk.END)
                        self.matrix_entries[i][j].insert(0, str(new_matrix[i, j]))
                result += "--- Удаление слабо доминируемых строк ---\n" + "\n".join(info) + "\n"
                result += f"Удалено {len(rows_to_remove)} строк\nНовая матрица:\n{new_matrix}\n"
            else:
                result += "Слабо доминируемых строк не найдено\n"
        else:  # player == "column"
            cols_to_remove = set()
            info = []
            for j in range(matrix.shape[1]):
                for l in range(matrix.shape[1]):
                    if j != l and (np.all(matrix[:, j] <= matrix[:, l]) and np.any(matrix[:, j] < matrix[:, l])):
                        cols_to_remove.add(j)
                        info.append(f"Столбец {j + 1} слабо доминируется столбцом {l + 1}")
                        info.append(f"Удален столбец {j + 1}")
            if cols_to_remove:
                new_matrix = np.delete(matrix, list(cols_to_remove), axis=1)
                self.cols.set(new_matrix.shape[1])
                self.update_matrix_input()
                for i in range(new_matrix.shape[0]):
                    for j in range(new_matrix.shape[1]):
                        self.matrix_entries[i][j].delete(0, tk.END)
                        self.matrix_entries[i][j].insert(0, str(new_matrix[i, j]))
                result += "--- Удаление слабо доминируемых столбцов ---\n" + "\n".join(info) + "\n"
                result += f"Удалено {len(cols_to_remove)} столбцов\nНовая матрица:\n{new_matrix}\n"
            else:
                result += "Слабо доминируемых столбцов не найдено\n"
        self.output_result(result)

    def output_result(self, message):
        if self.output_dest.get() == "results":
            self.result_text.insert(tk.END, f"[{get_current_timestamp()}] " + message)
            self.result_text.see(tk.END)
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                try:
                    with open(file_path, 'w') as file:
                        file.write(f"Результаты ({get_current_timestamp()}):\n\n")
                        file.write(message)
                    self.result_text.insert(tk.END, f"Результаты сохранены в {file_path}\n")
                    self.result_text.see(tk.END)
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")


# ---------------------------
# Вкладка для биматричных игр
# ---------------------------
class BiMatrixGameFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Для биматричных игр каждый элемент – пара значений (матрицы выигрышей для двух игроков)
        self.rows = tk.IntVar(value=2)
        self.cols = tk.IntVar(value=2)
        self.matrix_entries = []  # Каждый элемент: ((entry1, entry2), ...)
        self.output_dest = tk.StringVar(value="results")
        self.create_widgets()

    def create_widgets(self):
        top_frame = tk.Frame(self)
        top_frame.pack(padx=5, pady=5, fill=tk.X)

        # Размерность матрицы
        dim_frame = tk.LabelFrame(top_frame, text="Размерность матрицы", padx=5, pady=5)
        dim_frame.pack(side=tk.LEFT, padx=5)
        vcmd = (self.register(self.validate_spinbox), '%P')
        tk.Label(dim_frame, text="Rows:").grid(row=0, column=0, padx=2, pady=2)

        tk.Spinbox(dim_frame, from_=1, to=50, textvariable=self.rows, width=5,
                   validate="key", validatecommand=vcmd,
                   command=self.update_matrix_input).grid(row=0, column=1, padx=2, pady=2)
        tk.Label(dim_frame, text="Columns:").grid(row=0, column=2, padx=2, pady=2)
        tk.Spinbox(dim_frame, from_=1, to=50, textvariable=self.cols, width=5,
                   validate="key", validatecommand=vcmd,
                   command=self.update_matrix_input).grid(row=0, column=3, padx=2, pady=2)
        tk.Button(dim_frame, text="Обновить матрицу", command=self.update_matrix_input) \
            .grid(row=0, column=4, padx=5, pady=2)

        # Панель операций
        op_frame = tk.Frame(top_frame)
        op_frame.pack(side=tk.LEFT, padx=5)
        tk.Button(op_frame, text="Загрузить из файла", command=self.load_from_file) \
            .pack(side=tk.LEFT, padx=2)
        tk.Button(op_frame, text="Сохранить в файл", command=self.save_to_file) \
            .pack(side=tk.LEFT, padx=2)
        tk.Button(op_frame, text="Случайная матрица", command=self.generate_random) \
            .pack(side=tk.LEFT, padx=2)
        tk.Button(op_frame, text="Найти равновесие (Нэш)", command=self.find_nash_equilibrium) \
            .pack(side=tk.LEFT, padx=2)

        # Панель для удаления доминируемых стратегий
        dom_frame = tk.LabelFrame(self, text="Удаление доминируемых стратегий", padx=5, pady=5)
        dom_frame.pack(padx=5, pady=5, fill=tk.X)
        # Опция выбора игрока
        self.player_var = tk.StringVar(value="row")
        tk.Label(dom_frame, text="Игрок:").pack(side=tk.LEFT, padx=2)
        tk.OptionMenu(dom_frame, self.player_var, "row", "column").pack(side=tk.LEFT, padx=2)
        tk.Button(dom_frame, text="Удалить строго доминируемые", command=self.remove_strictly_dominated) \
            .pack(side=tk.LEFT, padx=5)
        tk.Button(dom_frame, text="Удалить слабо доминируемые", command=self.remove_weakly_dominated) \
            .pack(side=tk.LEFT, padx=5)

        # Выбор места вывода
        output_frame = tk.Frame(self)
        output_frame.pack(padx=5, pady=5, fill=tk.X)
        tk.Label(output_frame, text="Output:").pack(side=tk.LEFT)
        tk.Radiobutton(output_frame, text="Results", variable=self.output_dest, value="results") \
            .pack(side=tk.LEFT)
        tk.Radiobutton(output_frame, text="File", variable=self.output_dest, value="file") \
            .pack(side=tk.LEFT)

        # Панель ввода матрицы (каждая ячейка – пара значений, разделённых символом ;)
        self.matrix_input_frame = tk.LabelFrame(self, text="Биматричная игра (A;B)", padx=5, pady=5)
        self.matrix_input_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.update_matrix_input()

        # Текст для вывода результатов
        self.result_text = tk.Text(self, height=10, wrap=tk.WORD)
        self.result_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def validate_spinbox(self, value_if_allowed):
        # Разрешаем пустую строку (пока пользователь не ввёл число)
        if value_if_allowed == "":
            return True
        try:
            val = int(value_if_allowed)
            return 1 <= val <= 50
        except ValueError:
            return False

    def update_matrix_input(self):
        for widget in self.matrix_input_frame.winfo_children():
            widget.destroy()
        self.matrix_entries = []
        rows = self.rows.get()
        cols = self.cols.get()
        if rows == 1 and cols == 1:
            messagebox.showerror("Ошибка",
                                 "Биматрица не может быть размером 1x1!\nДопустимые размеры: 1x2, 2x1 или NxN.")
            self.cols.set(2)
            cols = 2
        # Заголовки столбцов
        for j in range(cols):
            tk.Label(self.matrix_input_frame, text=f"Col {j + 1}").grid(row=0, column=j + 1, padx=2, pady=2)
        # Поля ввода
        for i in range(rows):
            tk.Label(self.matrix_input_frame, text=f"Row {i + 1}").grid(row=i + 1, column=0, padx=2, pady=2)
            row_entries = []
            for j in range(cols):
                cell_frame = tk.Frame(self.matrix_input_frame)
                cell_frame.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                entry1 = tk.Entry(cell_frame, width=5)
                entry1.pack(side=tk.LEFT)
                tk.Label(cell_frame, text=";").pack(side=tk.LEFT)
                entry2 = tk.Entry(cell_frame, width=5)
                entry2.pack(side=tk.LEFT)
                entry1.insert(0, "0")
                entry2.insert(0, "0")
                row_entries.append((entry1, entry2))
            self.matrix_entries.append(row_entries)

    def get_matrices(self):
        matrix1 = []
        matrix2 = []
        try:
            for i in range(self.rows.get()):
                row1 = []
                row2 = []
                for j in range(self.cols.get()):
                    val1 = float(self.matrix_entries[i][j][0].get())
                    val2 = float(self.matrix_entries[i][j][1].get())
                    row1.append(val1)
                    row2.append(val2)
                matrix1.append(row1)
                matrix2.append(row2)
            return np.array(matrix1), np.array(matrix2)
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа в ячейки")
            return None, None

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'r') as file:
                lines = [line.strip() for line in file if line.strip()]
            if not lines:
                messagebox.showerror("Ошибка", "Файл пуст!\n")
                return

            # Парсинг размеров матрицы
            try:
                dims = list(map(int, lines[0].split()))
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат размеров матрицы в файле!")
                return
            if len(dims) != 2:
                messagebox.showerror("Ошибка", "Первая строка должна содержать ровно два числа (строки и столбцы)!")
                return
            rows, cols = dims
            if rows < 1 or cols < 1:
                messagebox.showerror("Ошибка", "Размеры матрицы должны быть положительными!")
                return
            if rows == 1 and cols == 1:
                messagebox.showerror("Ошибка",
                                     "Биматрица из файла не может быть размером 1x1!\nДопустимые размеры: 1x2, 2x1 или NxN.")
                return
            if rows > 20 or cols > 20:
                messagebox.showerror("Ошибка", "Максимальная размерность матрицы - 20x20!")
                return

            # Для биматричной игры должно быть 1 + 2*rows строк
            if len(lines) < 1 + 2 * rows:
                messagebox.showerror("Ошибка", "В файле недостаточно строк для биматричной игры!")
                return

            matrix1 = []
            matrix2 = []
            for idx in range(rows):
                try:
                    vals = list(map(float, lines[1 + idx].split()))
                except ValueError:
                    messagebox.showerror("Ошибка", f"Некорректный ввод данных в строке {2 + idx} (ожидались числа)!")
                    return
                if len(vals) != cols:
                    messagebox.showerror("Ошибка", f"В строке {2 + idx} должно быть {cols} чисел, найдено {len(vals)}!")
                    return
                matrix1.append(vals)
            for idx in range(rows):
                try:
                    vals = list(map(float, lines[1 + rows + idx].split()))
                except ValueError:
                    messagebox.showerror("Ошибка",
                                         f"Некорректный ввод данных в строке {2 + rows + idx} (ожидались числа)!")
                    return
                if len(vals) != cols:
                    messagebox.showerror("Ошибка",
                                         f"В строке {2 + rows + idx} должно быть {cols} чисел, найдено {len(vals)}!")
                    return
                matrix2.append(vals)

            self.rows.set(rows)
            self.cols.set(cols)
            self.update_matrix_input()
            for i in range(rows):
                for j in range(cols):
                    self.matrix_entries[i][j][0].delete(0, tk.END)
                    self.matrix_entries[i][j][0].insert(0, str(matrix1[i][j]))
                    self.matrix_entries[i][j][1].delete(0, tk.END)
                    self.matrix_entries[i][j][1].insert(0, str(matrix2[i][j]))
            self.output_result(f"Биматрица успешно загружена из {file_path}\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {str(e)}")

    def save_to_file(self):
        matrix1, matrix2 = self.get_matrices()
        if matrix1 is None or matrix2 is None:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'w') as file:
                file.write(f"{self.rows.get()} {self.cols.get()}\n")
                for row in matrix1:
                    file.write(" ".join(map(str, row)) + "\n")
                for row in matrix2:
                    file.write(" ".join(map(str, row)) + "\n")
            self.output_result(f"Биматрица сохранена в {file_path}\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения файла: {str(e)}")

    def generate_random(self):
        rows = self.rows.get()
        cols = self.cols.get()
        for i in range(rows):
            for j in range(cols):
                self.matrix_entries[i][j][0].delete(0, tk.END)
                self.matrix_entries[i][j][0].insert(0, str(random.randint(-10, 10)))
                self.matrix_entries[i][j][1].delete(0, tk.END)
                self.matrix_entries[i][j][1].insert(0, str(random.randint(-10, 10)))
        self.output_result(f"Сгенерирована случайная биматрица {rows}x{cols}\n")

    def find_nash_equilibrium(self):
        matrix1, matrix2 = self.get_matrices()
        if matrix1 is None or matrix2 is None:
            return
        try:
            nash_equilibria = []
            rows, cols = self.rows.get(), self.cols.get()
            for i in range(rows):
                for j in range(cols):
                    is_nash = True
                    # Для игрока 1: сравниваем значения из matrix1
                    for k in range(rows):
                        if matrix1[k, j] > matrix1[i, j]:
                            is_nash = False
                            break
                    if is_nash:
                        # Для игрока 2: сравниваем значения из matrix2
                        for l in range(cols):
                            if matrix2[i, l] > matrix2[i, j]:
                                is_nash = False
                                break
                    if is_nash:
                        nash_equilibria.append((i + 1, j + 1))
            if nash_equilibria:
                eq_str = "\n".join([f"(Row {r}, Column {c})" for r, c in nash_equilibria])
                result = f"Найдено {len(nash_equilibria)} равновесие(я):\n" + eq_str + "\n"
            else:
                result = "В чистых стратегиях равновесие Нэша не найдено\n"
            self.output_result(result)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска равновесия: {str(e)}")

    def remove_strictly_dominated(self):
        # Для биматричных игр удаляем стратегии для выбранного игрока отдельно,
        # используя соответствующую матрицу выигрышей
        matrix1, matrix2 = self.get_matrices()
        if matrix1 is None or matrix2 is None:
            return
        player = self.player_var.get()
        result = ""
        if player == "row":
            rows_to_remove = set()
            info = []
            for i in range(matrix1.shape[0]):
                for k in range(matrix1.shape[0]):
                    if i != k and np.all(matrix1[i, :] < matrix1[k, :]):
                        rows_to_remove.add(i)
                        info.append(f"Строка {i + 1} строго доминируется строкой {k + 1}")
                        info.append(f"Удалена строка {i + 1}")
            if rows_to_remove:
                new_m1 = np.delete(matrix1, list(rows_to_remove), axis=0)
                new_m2 = np.delete(matrix2, list(rows_to_remove), axis=0)
                self.rows.set(new_m1.shape[0])
                self.update_matrix_input()
                for i in range(new_m1.shape[0]):
                    for j in range(new_m1.shape[1]):
                        self.matrix_entries[i][j][0].delete(0, tk.END)
                        self.matrix_entries[i][j][0].insert(0, str(new_m1[i, j]))
                        self.matrix_entries[i][j][1].delete(0, tk.END)
                        self.matrix_entries[i][j][1].insert(0, str(new_m2[i, j]))
                result += "--- Удаление строго доминируемых строк (игрок 1) ---\n" + "\n".join(info) + "\n"
            else:
                result += "Строго доминируемых строк не найдено\n"
        else:  # column
            cols_to_remove = set()
            info = []
            for j in range(matrix2.shape[1]):
                for l in range(matrix2.shape[1]):
                    if j != l and np.all(matrix2[:, j] < matrix2[:, l]):
                        cols_to_remove.add(j)
                        info.append(f"Столбец {j + 1} строго доминируется столбцом {l + 1}")
                        info.append(f"Удален столбец {j + 1}")
            if cols_to_remove:
                new_m1 = np.delete(matrix1, list(cols_to_remove), axis=1)
                new_m2 = np.delete(matrix2, list(cols_to_remove), axis=1)
                self.cols.set(new_m1.shape[1])
                self.update_matrix_input()
                for i in range(new_m1.shape[0]):
                    for j in range(new_m1.shape[1]):
                        self.matrix_entries[i][j][0].delete(0, tk.END)
                        self.matrix_entries[i][j][0].insert(0, str(new_m1[i, j]))
                        self.matrix_entries[i][j][1].delete(0, tk.END)
                        self.matrix_entries[i][j][1].insert(0, str(new_m2[i, j]))
                result += "--- Удаление строго доминируемых столбцов (игрок 2) ---\n" + "\n".join(info) + "\n"
            else:
                result += "Строго доминируемых столбцов не найдено\n"
        self.output_result(result)

    def remove_weakly_dominated(self):
        matrix1, matrix2 = self.get_matrices()
        if matrix1 is None or matrix2 is None:
            return
        player = self.player_var.get()
        result = ""
        if player == "row":
            rows_to_remove = set()
            info = []
            for i in range(matrix1.shape[0]):
                for k in range(matrix1.shape[0]):
                    if i != k and (np.all(matrix1[i, :] <= matrix1[k, :]) and np.any(matrix1[i, :] < matrix1[k, :])):
                        rows_to_remove.add(i)
                        info.append(f"Строка {i + 1} слабо доминируется строкой {k + 1}")
                        info.append(f"Удалена строка {i + 1}")
            if rows_to_remove:
                new_m1 = np.delete(matrix1, list(rows_to_remove), axis=0)
                new_m2 = np.delete(matrix2, list(rows_to_remove), axis=0)
                self.rows.set(new_m1.shape[0])
                self.update_matrix_input()
                for i in range(new_m1.shape[0]):
                    for j in range(new_m1.shape[1]):
                        self.matrix_entries[i][j][0].delete(0, tk.END)
                        self.matrix_entries[i][j][0].insert(0, str(new_m1[i, j]))
                        self.matrix_entries[i][j][1].delete(0, tk.END)
                        self.matrix_entries[i][j][1].insert(0, str(new_m2[i, j]))
                result += "--- Удаление слабо доминируемых строк (игрок 1) ---\n" + "\n".join(info) + "\n"
            else:
                result += "Слабо доминируемых строк не найдено\n"
        else:
            cols_to_remove = set()
            info = []
            for j in range(matrix2.shape[1]):
                for l in range(matrix2.shape[1]):
                    if j != l and (np.all(matrix2[:, j] <= matrix2[:, l]) and np.any(matrix2[:, j] < matrix2[:, l])):
                        cols_to_remove.add(j)
                        info.append(f"Столбец {j + 1} слабо доминируется столбцом {l + 1}")
                        info.append(f"Удален столбец {j + 1}")
            if cols_to_remove:
                new_m1 = np.delete(matrix1, list(cols_to_remove), axis=1)
                new_m2 = np.delete(matrix2, list(cols_to_remove), axis=1)
                self.cols.set(new_m1.shape[1])
                self.update_matrix_input()
                for i in range(new_m1.shape[0]):
                    for j in range(new_m1.shape[1]):
                        self.matrix_entries[i][j][0].delete(0, tk.END)
                        self.matrix_entries[i][j][0].insert(0, str(new_m1[i, j]))
                        self.matrix_entries[i][j][1].delete(0, tk.END)
                        self.matrix_entries[i][j][1].insert(0, str(new_m2[i, j]))
                result += "--- Удаление слабо доминируемых столбцов (игрок 2) ---\n" + "\n".join(info) + "\n"
            else:
                result += "Слабо доминируемых столбцов не найдено\n"
        self.output_result(result)

    def output_result(self, message):
        if self.output_dest.get() == "results":
            self.result_text.insert(tk.END, f"[{get_current_timestamp()}] " + message)
            self.result_text.see(tk.END)
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                try:
                    with open(file_path, 'w') as file:
                        file.write(f"Результаты ({get_current_timestamp()}):\n\n")
                        file.write(message)
                    self.result_text.insert(tk.END, f"Результаты сохранены в {file_path}\n")
                    self.result_text.see(tk.END)
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")


# ---------------------------
# Главное окно с вкладками
# ---------------------------
class GameTheoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Алгоритмы теории игр")
        self.geometry("900x600")  # Можно закомментировать, чтобы окно авто-подстраивалось

        # Разрешаем пользователю изменять размер окна
        self.resizable(True, True)

        # ----- Верхний фрейм, который займёт всю доступную область по вертикали -----
        main_frame = tk.Frame(self)
        main_frame.pack(side="top", fill="both", expand=True)

        # ----- Canvas и вертикальный скроллбар -----
        canvas = tk.Canvas(main_frame)
        canvas.pack(side="left", fill="both", expand=True)

        v_scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=v_scrollbar.set)

        # ----- Горизонтальный скроллбар внизу окна (растягивается на всю ширину) -----
        h_scrollbar = tk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.configure(xscrollcommand=h_scrollbar.set)

        # ----- Фрейм внутри Canvas, который прокручивается -----
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # ----- Notebook внутри прокручиваемого фрейма -----
        notebook = ttk.Notebook(scrollable_frame)
        notebook.pack(fill="both", expand=True)

        # Предположим, что у вас есть два класса: MatrixGameFrame и BiMatrixGameFrame
        self.matrix_game_frame = MatrixGameFrame(notebook)
        notebook.add(self.matrix_game_frame, text="Матричные игры")

        self.bimatrix_game_frame = BiMatrixGameFrame(notebook)
        notebook.add(self.bimatrix_game_frame, text="Биматричные игры")


if __name__ == "__main__":
    app = GameTheoryApp()
    app.mainloop()
