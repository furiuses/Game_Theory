import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import random
from datetime import datetime


class NashEquilibriumWindow:
    def __init__(self, parent, rows=2, cols=2):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Nash Equilibrium - Bimatrix Game")

        self.rows = rows
        self.cols = cols
        self.matrix_entries = []
        self.matrix1 = None
        self.matrix2 = None

        self.create_widgets()

    def create_widgets(self):
        # Фрейм для кнопок управления
        control_frame = tk.Frame(self.window)
        control_frame.pack(padx=10, pady=5, fill=tk.X)

        tk.Button(control_frame, text="Load from File", command=self.load_from_file).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Save to File", command=self.save_to_file).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Generate Random", command=self.generate_random).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Find Equilibrium", command=self.find_equilibrium).pack(side=tk.LEFT, padx=5)

        # Фрейм для изменения размеров матрицы
        dimension_frame = tk.LabelFrame(self.window, text="Matrix Dimensions", padx=5, pady=5)
        dimension_frame.pack(padx=10, pady=5, fill=tk.X)

        tk.Label(dimension_frame, text="Rows:").grid(row=0, column=0, padx=5, pady=2)
        self.rows_spinbox = tk.Spinbox(dimension_frame, from_=1, to=10, width=5,
                                       command=lambda: self.update_matrix_size(self.rows_spinbox.get(),
                                                                               self.cols_spinbox.get()))
        self.rows_spinbox.grid(row=0, column=1, padx=5, pady=2)
        self.rows_spinbox.delete(0, tk.END)
        self.rows_spinbox.insert(0, str(self.rows))

        tk.Label(dimension_frame, text="Columns:").grid(row=0, column=2, padx=5, pady=2)
        self.cols_spinbox = tk.Spinbox(dimension_frame, from_=1, to=10, width=5,
                                       command=lambda: self.update_matrix_size(self.rows_spinbox.get(),
                                                                               self.cols_spinbox.get()))
        self.cols_spinbox.grid(row=0, column=3, padx=5, pady=2)
        self.cols_spinbox.delete(0, tk.END)
        self.cols_spinbox.insert(0, str(self.cols))

        tk.Button(dimension_frame, text="Update Size",
                  command=lambda: self.update_matrix_size(self.rows_spinbox.get(), self.cols_spinbox.get())).grid(row=0,
                                                                                                                  column=4,
                                                                                                                  padx=5)

        # Фрейм для ввода матрицы
        matrix_frame = tk.LabelFrame(self.window, text="Bimatrix Game", padx=5, pady=5)
        matrix_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.matrix_input_frame = tk.Frame(matrix_frame)
        self.matrix_input_frame.pack(fill=tk.BOTH, expand=True)

        # Фрейм для результатов
        result_frame = tk.LabelFrame(self.window, text="Results", padx=5, pady=5)
        result_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(result_frame, height=5, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        self.update_matrix_input()

    def update_matrix_size(self, rows, cols):
        """Обновляет размеры матрицы"""
        try:
            new_rows = int(rows)
            new_cols = int(cols)

            if new_rows < 1 or new_cols < 1:
                raise ValueError("Dimensions must be positive integers")

            self.rows = new_rows
            self.cols = new_cols
            self.update_matrix_input()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid positive integers for matrix dimensions")
            # Reset spinboxes to current values
            self.rows_spinbox.delete(0, tk.END)
            self.rows_spinbox.insert(0, str(self.rows))
            self.cols_spinbox.delete(0, tk.END)
            self.cols_spinbox.insert(0, str(self.cols))

    def update_matrix_input(self):
        """Обновляет поля ввода матрицы"""
        for widget in self.matrix_input_frame.winfo_children():
            widget.destroy()

        self.matrix_entries = []

        # Создаем заголовки столбцов
        for j in range(self.cols):
            tk.Label(self.matrix_input_frame, text=f"Col {j + 1}").grid(row=0, column=j + 1, padx=5, pady=2)

        # Создаем поля ввода для матрицы
        for i in range(self.rows):
            tk.Label(self.matrix_input_frame, text=f"Row {i + 1}").grid(row=i + 1, column=0, padx=5, pady=2)
            row_entries = []
            for j in range(self.cols):
                cell_frame = tk.Frame(self.matrix_input_frame)
                cell_frame.grid(row=i + 1, column=j + 1, padx=5, pady=2)

                entry1 = tk.Entry(cell_frame, width=5)
                entry1.pack(side=tk.LEFT)
                entry1.insert(0, "0")

                tk.Label(cell_frame, text=";").pack(side=tk.LEFT)

                entry2 = tk.Entry(cell_frame, width=5)
                entry2.pack(side=tk.LEFT)
                entry2.insert(0, "0")

                row_entries.append((entry1, entry2))
            self.matrix_entries.append(row_entries)

    def get_matrices(self):
        """Получает матрицы из полей ввода"""
        matrix1 = []
        matrix2 = []

        try:
            for i in range(self.rows):
                row1 = []
                row2 = []
                for j in range(self.cols):
                    value1 = float(self.matrix_entries[i][j][0].get())
                    value2 = float(self.matrix_entries[i][j][1].get())
                    row1.append(value1)
                    row2.append(value2)
                matrix1.append(row1)
                matrix2.append(row2)
            return np.array(matrix1), np.array(matrix2)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers in all matrix cells")
            return None, None

    def load_from_file(self):
        """Загружает матрицу из файла"""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]

                if len(lines) < 2:
                    raise ValueError("File should contain at least 2 lines")

                # Первая строка - размеры матрицы
                dimensions = list(map(int, lines[0].split()))
                if len(dimensions) != 2:
                    raise ValueError("First line should contain two numbers: rows and columns")

                rows, cols = dimensions
                self.rows = rows
                self.cols = cols
                self.update_matrix_input()

                if len(lines) < 1 + 2 * rows:
                    raise ValueError(f"Expected {2 * rows} lines of matrix data")

                # Загружаем первую матрицу
                for i in range(rows):
                    values = list(map(float, lines[i + 1].split()))
                    if len(values) != cols:
                        raise ValueError(f"Row {i + 1} has incorrect number of elements")
                    for j in range(cols):
                        self.matrix_entries[i][j][0].delete(0, tk.END)
                        self.matrix_entries[i][j][0].insert(0, str(values[j]))

                # Загружаем вторую матрицу
                for i in range(rows):
                    values = list(map(float, lines[i + 1 + rows].split()))
                    if len(values) != cols:
                        raise ValueError(f"Row {i + 1 + rows} has incorrect number of elements")
                    for j in range(cols):
                        self.matrix_entries[i][j][1].delete(0, tk.END)
                        self.matrix_entries[i][j][1].insert(0, str(values[j]))

                self.add_result(f"Bimatrix loaded from {file_path}\n")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def save_to_file(self):
        """Сохраняет матрицу в файл"""
        matrix1, matrix2 = self.get_matrices()
        if matrix1 is None or matrix2 is None:
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, 'w') as file:
                # Записываем размеры матрицы
                file.write(f"{self.rows} {self.cols}\n")

                # Записываем первую матрицу
                for row in matrix1:
                    file.write(" ".join(map(str, row)) + "\n")

                # Записываем вторую матрицу
                for row in matrix2:
                    file.write(" ".join(map(str, row)) + "\n")

            self.add_result(f"Bimatrix saved to {file_path}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def generate_random(self):
        """Генерирует случайные значения для матриц"""
        for i in range(self.rows):
            for j in range(self.cols):
                self.matrix_entries[i][j][0].delete(0, tk.END)
                self.matrix_entries[i][j][0].insert(0, str(random.randint(-10, 10)))
                self.matrix_entries[i][j][1].delete(0, tk.END)
                self.matrix_entries[i][j][1].insert(0, str(random.randint(-10, 10)))

        self.add_result(f"Generated random {self.rows}x{self.cols} bimatrix\n")

    def find_equilibrium(self):
        """Находит равновесия Нэша в чистых стратегиях"""
        matrix1, matrix2 = self.get_matrices()
        if matrix1 is None or matrix2 is None:
            return

        try:
            nash_equilibria = []

            for i in range(self.rows):
                for j in range(self.cols):
                    is_nash = True

                    # Проверяем для первого игрока
                    for k in range(self.rows):
                        if matrix1[k, j] > matrix1[i, j]:
                            is_nash = False
                            break

                    # Проверяем для второго игрока
                    if is_nash:
                        for l in range(self.cols):
                            if matrix2[i, l] > matrix2[i, j]:
                                is_nash = False
                                break

                    if is_nash:
                        nash_equilibria.append((i + 1, j + 1))  # +1 для индексации с 1

            if not nash_equilibria:
                result = "No Nash equilibria found in pure strategies\n"
            else:
                equilibria_str = "\n".join([f"(Row {row}, Column {col})" for row, col in nash_equilibria])
                result = (
                        "--- Nash Equilibria in Pure Strategies ---\n" +
                        f"Found {len(nash_equilibria)} equilibrium(s):\n" +
                        equilibria_str + "\n"
                )

            self.add_result(result)

        except Exception as e:
            messagebox.showerror("Error", f"Error in finding Nash equilibrium: {str(e)}")

    def add_result(self, message):
        """Добавляет сообщение в результаты"""
        self.result_text.insert(tk.END, message)
        self.result_text.see(tk.END)

class GameTheoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Theory Algorithms")

        # Переменные для хранения данных
        self.rows = tk.IntVar(value=2)
        self.cols = tk.IntVar(value=2)
        self.matrix_entries = []
        self.matrix = None
        self.history = []
        self.output_dest = tk.StringVar(value="results")  # "results" или "file"

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Фрейм для ввода размерности матрицы
        dimension_frame = tk.LabelFrame(self.root, text="Matrix Dimensions", padx=5, pady=5)
        dimension_frame.pack(padx=10, pady=5, fill=tk.X)

        tk.Label(dimension_frame, text="Rows:").grid(row=0, column=0, padx=5, pady=5)
        tk.Spinbox(dimension_frame, from_=1, to=10, textvariable=self.rows, width=5,
                   command=self.update_matrix_input).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dimension_frame, text="Columns:").grid(row=0, column=2, padx=5, pady=5)
        tk.Spinbox(dimension_frame, from_=1, to=10, textvariable=self.cols, width=5,
                   command=self.update_matrix_input).grid(row=0, column=3, padx=5, pady=5)

        # Кнопка обновления матрицы
        tk.Button(dimension_frame, text="Update Matrix", command=self.update_matrix_input).grid(row=0, column=4,
                                                                                                padx=10)

        # Фрейм для ввода матрицы
        matrix_frame = tk.LabelFrame(self.root, text="Payoff Matrix", padx=5, pady=5)
        matrix_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.matrix_input_frame = tk.Frame(matrix_frame)
        self.matrix_input_frame.pack(fill=tk.BOTH, expand=True)

        # Фрейм для кнопок операций
        button_frame = tk.Frame(self.root)
        button_frame.pack(padx=10, pady=5, fill=tk.X)

        # Кнопки ввода/вывода
        tk.Button(button_frame, text="Load Matrix", command=self.load_from_file).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save Matrix", command=self.save_matrix_to_file).pack(side=tk.LEFT, padx=5)

        # Фрейм для алгоритмов и вывода
        algo_frame = tk.Frame(button_frame)
        algo_frame.pack(side=tk.LEFT, padx=5)

        # Выбор места вывода результатов
        output_frame = tk.Frame(algo_frame)
        output_frame.pack(fill=tk.X, pady=2)
        tk.Label(output_frame, text="Output:").pack(side=tk.LEFT)
        tk.Radiobutton(output_frame, text="Results", variable=self.output_dest, value="results").pack(side=tk.LEFT)
        tk.Radiobutton(output_frame, text="File", variable=self.output_dest, value="file").pack(side=tk.LEFT)

        # Кнопки алгоритмов
        tk.Button(algo_frame, text="Maximin/Minimax", command=self.find_maximin_minimax).pack(fill=tk.X, pady=2)

        # Фрейм для удаления стратегий
        remove_frame = tk.Frame(algo_frame)
        remove_frame.pack(fill=tk.X)

        self.player_var = tk.StringVar(value="row")
        tk.OptionMenu(remove_frame, self.player_var, "row", "column").pack(side=tk.LEFT)
        tk.Button(remove_frame, text="Remove Strictly Dominated", command=self.remove_strictly_dominated).pack(
            side=tk.LEFT)
        tk.Button(remove_frame, text="Remove Weakly Dominated", command=self.remove_weakly_dominated).pack(side=tk.LEFT)
        tk.Button(remove_frame, text="Find Nash Equilibrium", command=self.open_nash_window).pack(side=tk.LEFT)

        # Фрейм для вывода результатов
        result_frame = tk.LabelFrame(self.root, text="Results", padx=5, pady=5)
        result_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Кнопки управления историей
        history_btn_frame = tk.Frame(result_frame)
        history_btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(history_btn_frame, text="Save History", command=self.save_history_to_file).pack(side=tk.LEFT, padx=5)
        tk.Button(history_btn_frame, text="Clear History", command=self.clear_history).pack(side=tk.LEFT, padx=5)

        self.result_text = tk.Text(result_frame, height=10, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Инициализация полей ввода матрицы
        self.update_matrix_input()

    def open_nash_window(self):
        """Открывает окно для поиска равновесия Нэша"""
        NashEquilibriumWindow(self.root, self.rows.get(), self.cols.get())

    def output_result(self, message):
        """Выводит результат в выбранное место"""
        if self.output_dest.get() == "results":
            self.add_to_history(message)
        else:
            self.save_result_to_file(message)

    def save_result_to_file(self, message):
        """Сохраняет результат в файл"""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, 'w') as file:
                file.write(f"Game Theory Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                file.write(message)

            self.add_to_history(f"Results saved to {file_path}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")

    def update_matrix_input(self):
        """Обновляет поля ввода матрицы согласно выбранным размерам"""
        # Удаляем старые поля ввода
        for widget in self.matrix_input_frame.winfo_children():
            widget.destroy()

        rows = self.rows.get()
        cols = self.cols.get()
        self.matrix_entries = []

        # Создаем заголовки столбцов
        for j in range(cols):
            tk.Label(self.matrix_input_frame, text=f"Col {j + 1}").grid(row=0, column=j + 1, padx=5, pady=2)

        # Создаем поля ввода для матрицы
        for i in range(rows):
            tk.Label(self.matrix_input_frame, text=f"Row {i + 1}").grid(row=i + 1, column=0, padx=5, pady=2)
            row_entries = []
            for j in range(cols):
                entry = tk.Entry(self.matrix_input_frame, width=8)
                entry.grid(row=i + 1, column=j + 1, padx=5, pady=2)
                entry.insert(0, "0")  # По умолчанию заполняем нулями
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)

    def get_matrix_from_input(self):
        """Получает матрицу из полей ввода"""
        rows = self.rows.get()
        cols = self.cols.get()
        matrix = []

        try:
            for i in range(rows):
                row = []
                for j in range(cols):
                    value = float(self.matrix_entries[i][j].get())
                    row.append(value)
                matrix.append(row)
            return np.array(matrix)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers in all matrix cells")
            return None

    def load_from_file(self):
        """Загружает матрицу из файла"""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                if len(lines) < 2:
                    raise ValueError("File should contain at least 2 lines")

                # Первая строка - размеры матрицы
                dimensions = list(map(int, lines[0].strip().split()))
                if len(dimensions) != 2:
                    raise ValueError("First line should contain two numbers: rows and columns")

                rows, cols = dimensions
                self.rows.set(rows)
                self.cols.set(cols)
                self.update_matrix_input()

                # Последующие строки - элементы матрицы
                for i in range(1, min(rows + 1, len(lines))):
                    values = list(map(float, lines[i].strip().split()))
                    if len(values) != cols:
                        raise ValueError(f"Row {i} has incorrect number of elements")

                    for j in range(cols):
                        self.matrix_entries[i - 1][j].delete(0, tk.END)
                        self.matrix_entries[i - 1][j].insert(0, str(values[j]))

                self.add_to_history(f"Matrix loaded from {file_path}\n")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def save_matrix_to_file(self):
        """Сохраняет матрицу в файл"""
        matrix = self.get_matrix_from_input()
        if matrix is None:
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, 'w') as file:
                # Записываем размеры матрицы
                file.write(f"{self.rows.get()} {self.cols.get()}\n")

                # Записываем саму матрицу
                for row in matrix:
                    file.write(" ".join(map(str, row)) + "\n")

            self.add_to_history(f"Matrix saved to {file_path}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def save_history_to_file(self):
        """Сохраняет историю результатов в файл"""
        history = self.result_text.get("1.0", tk.END)
        if not history.strip():
            messagebox.showwarning("Warning", "History is empty")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, 'w') as file:
                # Добавляем заголовок с датой и временем
                file.write(f"Game Theory Results History - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                file.write(history)

            self.add_to_history(f"History saved to {file_path}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save history: {str(e)}")

    def clear_history(self):
        """Очищает историю результатов"""
        self.result_text.delete("1.0", tk.END)
        self.add_to_history("History cleared\n")

    def add_to_history(self, message):
        """Добавляет сообщение в историю с временной меткой"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.result_text.insert(tk.END, f"[{timestamp}] {message}")
        self.result_text.see(tk.END)  # Автопрокрутка к новому сообщению

    def generate_random_matrix(self):
        """Генерирует случайную матрицу"""
        rows = self.rows.get()
        cols = self.cols.get()

        for i in range(rows):
            for j in range(cols):
                self.matrix_entries[i][j].delete(0, tk.END)
                self.matrix_entries[i][j].insert(0, str(random.randint(-10, 10)))

        self.add_to_history(f"Generated random {rows}x{cols} matrix with values from -10 to 10\n")

    def find_maximin_minimax(self):
        """Находит максиминную и минимаксную стратегии"""
        matrix = self.get_matrix_from_input()
        if matrix is None:
            return

        try:
            # Максимин (для игрока по строкам)
            row_minima = np.min(matrix, axis=1)
            maximin = np.max(row_minima)
            maximin_row = np.argmax(row_minima)

            # Минимакс (для игрока по столбцам)
            col_maxima = np.max(matrix, axis=0)
            minimax = np.min(col_maxima)
            minimax_col = np.argmin(col_maxima)

            # Проверка на седловую точку
            saddle_point = maximin == minimax
            saddle_text = "Saddle point exists (Maximin = Minimax)" if saddle_point else "No saddle point"

            # Вывод результатов
            result = (
                f"Maximin (for row player):\n"
                f"  Strategy: Row {maximin_row + 1}\n"
                f"  Value: {maximin}\n\n"
                f"Minimax (for column player):\n"
                f"  Strategy: Column {minimax_col + 1}\n"
                f"  Value: {minimax}\n\n"
                f"{saddle_text}\n"
            )

            self.add_to_history("--- Maximin/Minimax Results ---\n")
            self.add_to_history(result)

        except Exception as e:
            messagebox.showerror("Error", f"Error in calculation: {str(e)}")

    def remove_strictly_dominated(self):
        """Удаляет строго доминируемые стратегии для выбранного игрока"""
        matrix = self.get_matrix_from_input()
        if matrix is None:
            return

        try:
            player = self.player_var.get()
            result = ""

            if player == "row":
                # Удаление строго доминируемых строк (игрок 1)
                rows_to_remove = set()
                dominated_info = []

                for i in range(matrix.shape[0]):
                    for k in range(matrix.shape[0]):
                        if i != k and np.all(matrix[i, :] < matrix[k, :]):
                            rows_to_remove.add(i)
                            dominated_info.append(f"Row {i + 1} is strictly dominated by Row {k + 1}")

                if not rows_to_remove:
                    result = "No strictly dominated rows found\n"
                    self.output_result(result)
                    return

                # Создаем новую матрицу без доминируемых строк
                new_matrix = np.delete(matrix, list(rows_to_remove), axis=0)

                # Обновляем интерфейс
                self.rows.set(new_matrix.shape[0])
                self.update_matrix_input()

                # Заполняем новыми значениями
                for i in range(new_matrix.shape[0]):
                    for j in range(new_matrix.shape[1]):
                        self.matrix_entries[i][j].delete(0, tk.END)
                        self.matrix_entries[i][j].insert(0, str(new_matrix[i, j]))

                result = (
                        "--- Strictly Dominated Rows Removal ---\n" +
                        "\n".join(dominated_info) + "\n\n" +
                        f"Removed {len(rows_to_remove)} strictly dominated rows\n" +
                        "New matrix:\n" +
                        str(new_matrix) + "\n"
                )

            else:  # column player
                # Удаление строго доминируемых столбцов (игрок 2)
                cols_to_remove = set()
                dominated_info = []

                for j in range(matrix.shape[1]):
                    for l in range(matrix.shape[1]):
                        if j != l and np.all(matrix[:, j] < matrix[:, l]):
                            cols_to_remove.add(j)
                            dominated_info.append(f"Column {j + 1} is strictly dominated by Column {l + 1}")

                if not cols_to_remove:
                    result = "No strictly dominated columns found\n"
                    self.output_result(result)
                    return

                # Создаем новую матрицу без доминируемых столбцов
                new_matrix = np.delete(matrix, list(cols_to_remove), axis=1)

                # Обновляем интерфейс
                self.cols.set(new_matrix.shape[1])
                self.update_matrix_input()

                # Заполняем новыми значениями
                for i in range(new_matrix.shape[0]):
                    for j in range(new_matrix.shape[1]):
                        self.matrix_entries[i][j].delete(0, tk.END)
                        self.matrix_entries[i][j].insert(0, str(new_matrix[i, j]))

                result = (
                        "--- Strictly Dominated Columns Removal ---\n" +
                        "\n".join(dominated_info) + "\n\n" +
                        f"Removed {len(cols_to_remove)} strictly dominated columns\n" +
                        "New matrix:\n" +
                        str(new_matrix) + "\n"
                )

            self.output_result(result)

        except Exception as e:
            messagebox.showerror("Error", f"Error in removing strictly dominated strategies: {str(e)}")

    def remove_weakly_dominated(self):
        """Удаляет слабо доминируемые стратегии для выбранного игрока"""
        matrix = self.get_matrix_from_input()
        if matrix is None:
            return

        try:
            player = self.player_var.get()
            result = ""

            if player == "row":
                # Удаление слабо доминируемых строк (игрок 1)
                rows_to_remove = set()
                dominated_info = []

                for i in range(matrix.shape[0]):
                    for k in range(matrix.shape[0]):
                        if i != k and (np.all(matrix[i, :] <= matrix[k, :]) and
                                       np.any(matrix[i, :] < matrix[k, :])):
                            rows_to_remove.add(i)
                            dominated_info.append(f"Row {i + 1} is weakly dominated by Row {k + 1}")

                if not rows_to_remove:
                    result = "No weakly dominated rows found\n"
                    self.output_result(result)
                    return

                # Создаем новую матрицу без доминируемых строк
                new_matrix = np.delete(matrix, list(rows_to_remove), axis=0)

                # Обновляем интерфейс
                self.rows.set(new_matrix.shape[0])
                self.update_matrix_input()

                # Заполняем новыми значениями
                for i in range(new_matrix.shape[0]):
                    for j in range(new_matrix.shape[1]):
                        self.matrix_entries[i][j].delete(0, tk.END)
                        self.matrix_entries[i][j].insert(0, str(new_matrix[i, j]))

                result = (
                        "--- Weakly Dominated Rows Removal ---\n" +
                        "\n".join(dominated_info) + "\n\n" +
                        f"Removed {len(rows_to_remove)} weakly dominated rows\n" +
                        "New matrix:\n" +
                        str(new_matrix) + "\n"
                )

            else:  # column player
                # Удаление слабо доминируемых столбцов (игрок 2)
                cols_to_remove = set()
                dominated_info = []

                for j in range(matrix.shape[1]):
                    for l in range(matrix.shape[1]):
                        if j != l and (np.all(matrix[:, j] <= matrix[:, l]) and
                                       np.any(matrix[:, j] < matrix[:, l])):
                            cols_to_remove.add(j)
                            dominated_info.append(f"Column {j + 1} is weakly dominated by Column {l + 1}")

                if not cols_to_remove:
                    result = "No weakly dominated columns found\n"
                    self.output_result(result)
                    return

                # Создаем новую матрицу без доминируемых столбцов
                new_matrix = np.delete(matrix, list(cols_to_remove), axis=1)

                # Обновляем интерфейс
                self.cols.set(new_matrix.shape[1])
                self.update_matrix_input()

                # Заполняем новыми значениями
                for i in range(new_matrix.shape[0]):
                    for j in range(new_matrix.shape[1]):
                        self.matrix_entries[i][j].delete(0, tk.END)
                        self.matrix_entries[i][j].insert(0, str(new_matrix[i, j]))

                result = (
                        "--- Weakly Dominated Columns Removal ---\n" +
                        "\n".join(dominated_info) + "\n\n" +
                        f"Removed {len(cols_to_remove)} weakly dominated columns\n" +
                        "New matrix:\n" +
                        str(new_matrix) + "\n"
                )

            self.output_result(result)

        except Exception as e:
            messagebox.showerror("Error", f"Error in removing weakly dominated strategies: {str(e)}")

    def find_nash_equilibrium(self):
        """Находит равновесия Нэша в чистых стратегиях"""
        matrix = self.get_matrix_from_input()
        if matrix is None:
            return

        try:
            nash_equilibria = []
            rows, cols = matrix.shape[0], matrix.shape[1]

            # Проверяем все возможные комбинации стратегий
            for i in range(rows):
                for j in range(cols):
                    is_nash = True

                    # Проверяем, является ли текущая стратегия лучшим ответом для игрока 1
                    for k in range(rows):
                        if matrix[k, j, 0] > matrix[i, j, 0]:  # Сравниваем выигрыши первого игрока
                            is_nash = False
                            break

                    if is_nash:
                        # Проверяем, является ли текущая стратегия лучшим ответом для игрока 2
                        for l in range(cols):
                            if matrix[i, l, 1] > matrix[i, j, 1]:  # Сравниваем выигрыши второго игрока
                                is_nash = False
                                break

                    if is_nash:
                        nash_equilibria.append((i + 1, j + 1))  # +1 для удобства пользователя (индексация с 1)

            if not nash_equilibria:
                result = "No Nash equilibria found in pure strategies\n"
            else:
                equilibria_str = "\n".join([f"(Row {row}, Column {col})" for row, col in nash_equilibria])
                result = (
                        "--- Nash Equilibria in Pure Strategies ---\n" +
                        f"Found {len(nash_equilibria)} equilibrium(s):\n" +
                        equilibria_str + "\n"
                )

            self.output_result(result)

        except Exception as e:
            messagebox.showerror("Error", f"Error in finding Nash equilibrium: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GameTheoryApp(root)
    root.mainloop()