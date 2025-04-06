import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.widgets import RadioButtons
import traceback
import math

# --- Функции read_matrices_from_file и create_value_counts ---
# (Остаются без изменений, как в предыдущем ответе)
def read_matrices_from_file(filename):
    matrices = []
    try:
        with open(filename, 'r') as f:
            try: num_matrices = int(f.readline().strip())
            except ValueError: raise ValueError("Первая строка (количество матриц) не целое.")
            except EOFError: raise ValueError("Файл слишком короткий (нет кол-ва матриц).")
            try: matrix_size = int(f.readline().strip())
            except ValueError: raise ValueError("Вторая строка (размер матрицы) не целое.")
            except EOFError: raise ValueError("Файл слишком короткий (нет размера).")
            if num_matrices <= 0 or matrix_size <= 0: raise ValueError("Размеры должны быть > 0.")
            for i in range(num_matrices):
                rows = []
                for j in range(matrix_size):
                    line = f.readline()
                    if not line and j < matrix_size: raise ValueError(f"EOF при чтении стр {j+1} мат {i+1}.")
                    try:
                        row = list(map(float, line.strip().split()))
                        if len(row) != matrix_size: raise ValueError(f"Неверное кол-во эл. в стр {j+1} мат {i+1} ({len(row)} вместо {matrix_size}).")
                        rows.append(row)
                    except ValueError: raise ValueError(f"Ошибка числа в стр {j+1} мат {i+1}.")
                matrices.append(np.array(rows))
                if i < num_matrices - 1:
                    sep = f.readline()
                    if sep is None: raise ValueError(f"EOF после мат {i+1}, ждали разделитель.")
                    if sep.strip() != "": raise ValueError(f"Ждали пустую строку после мат {i+1}, получили: '{sep.strip()}'")
        if len(matrices) != num_matrices: print(f"Предупреждение: Прочитано {len(matrices)}, ожидалось {num_matrices}.")
    except FileNotFoundError: print(f"Ошибка: Файл '{filename}' не найден."); return None
    except ValueError as ve: print(f"Ошибка чтения: {ve}"); return None
    except Exception as e: print(f"Неожиданная ошибка: {e}"); traceback.print_exc(); return None
    return matrices

def create_value_counts(matrices):
    value_counts = []
    for matrix in matrices:
        flat = matrix.flatten(); filtered = flat[flat != -1]
        value_counts.append(dict(Counter(filtered)))
    return value_counts
# --- Конец неизменных функций ---

# --- Интерактивный график с увеличенными кнопками ---
def create_interactive_plot(value_counts):
    """Создание интерактивного графика с увеличенными радиокнопками снизу"""
    num_matrices = len(value_counts)
    if num_matrices == 0: print("Нет данных для отображения."); return

    # --- Настройка макета ---
    max_cols = 6; num_cols = min(num_matrices, max_cols)
    num_rows = math.ceil(num_matrices / num_cols)
    row_height = 0.07 # Увеличим высоту строки для больших кнопок
    widget_height = num_rows * row_height + 0.02
    bottom_margin = 0.1 + widget_height

    fig, ax = plt.subplots(figsize=(10, 7 + num_rows * 0.2)) # Увеличим высоту фигуры
    fig.subplots_adjust(bottom=bottom_margin + 0.03)
    rax = fig.add_axes([0.05, 0.05, 0.9, widget_height])
    rax.set_facecolor('#f0f0f0') # Слегка серый фон
    rax.set_xticks([]); rax.set_yticks([])
    for spine in rax.spines.values(): spine.set_visible(False)

    # --- Функция обновления графика (без изменений) ---
    def plot_matrix(matrix_idx):
        ax.clear()
        counts = value_counts[matrix_idx]
        if not counts:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center', fontsize=12, transform=ax.transAxes)
            ax.set_title(f'Матрица {matrix_idx+1} (нет данных)', fontsize=14)
            ax.set_xlabel('Значение'); ax.set_ylabel('Частота')
            ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.grid(True, linestyle='--', alpha=0.6)
            fig.canvas.draw_idle(); return

        sorted_items = sorted(counts.items())
        values = [item[0] for item in sorted_items]; frequencies = [item[1] for item in sorted_items]
        ax.scatter(values, frequencies, s=80, alpha=0.8, color='#007acc', edgecolors='black', linewidth=0.5)
        unique_freqs = sorted(list(set(frequencies)))
        for freq in unique_freqs: ax.axhline(y=freq, color='grey', linestyle=':', alpha=0.5, linewidth=1)
        ax.set_xlabel('Значение элемента матрицы (исключая -1)', fontsize=11)
        ax.set_ylabel('Частота появления', fontsize=11)
        ax.set_title(f'Распределение значений в Матрице {matrix_idx+1}', fontsize=14, pad=10)
        ax.set_xlim(-0.05, 1.05)
        min_freq = 0; max_freq = max(frequencies) if frequencies else 1
        ax.set_ylim(min_freq - max_freq * 0.05, max_freq * 1.15)
        if frequencies:
             unique_ints = sorted([f for f in unique_freqs if f == int(f)])
             if len(unique_ints) <= 10 and len(unique_ints)>0: ax.set_yticks(unique_ints)
             else:
                 ax.yaxis.get_major_locator().set_params(integer=True)
                 current_ylim = ax.get_ylim(); ax.set_ylim(bottom=max(0, current_ylim[0]))
        ax.grid(True, linestyle='--', alpha=0.5)
        for x, y in zip(values, frequencies): ax.text(x, y + max_freq * 0.03, f'{y}', ha='center', va='bottom', fontsize=9)
        fig.canvas.draw_idle()

    # --- Создание RadioButtons и ручное размещение ---
    labels = [f'Матрица {i+1}' for i in range(num_matrices)]
    radio = RadioButtons(rax, labels, active=0, activecolor='#007acc')

    button_props = []; label_props = []
    hoffset = 0.02; voffset = 0.05
    col_width = (1.0 - 2 * hoffset) / num_cols
    row_height_actual = (1.0 - 2 * voffset) / num_rows
    # --- ИЗМЕНЕНИЕ ЗДЕСЬ: Увеличиваем множитель для радиуса ---
    circle_radius = 0.45 * min(col_width / 3, row_height_actual / 2) # Стало 0.45 (было 0.3)
    label_fontsize = 10

    current_row = num_rows - 1; current_col = 0
    for i in range(num_matrices):
        x_center = hoffset + current_col * col_width + col_width / 2
        y_center = voffset + current_row * row_height_actual + row_height_actual / 2
        button_props.append((x_center, y_center))

        x_label = x_center
        # --- ИЗМЕНЕНИЕ ЗДЕСЬ: Увеличиваем множитель для смещения метки ---
        y_label = y_center - circle_radius * 3.0 # Стало 3.0 (было 2.5)
        label_props.append((x_label, y_label))

        current_col += 1
        if current_col >= num_cols: current_col = 0; current_row -= 1

    for i, (circle, label) in enumerate(zip(radio.circles, radio.labels)):
        circle.center = button_props[i]
        circle.set_radius(circle_radius) # Применяем увеличенный радиус
        circle.set_linewidth(1.5)
        label.set_position(label_props[i])
        label.set_fontsize(label_fontsize)
        label.set_horizontalalignment('center')
        label.set_verticalalignment('top')

    def matrix_select(label):
        matrix_idx = labels.index(label); plot_matrix(matrix_idx)

    radio.on_clicked(matrix_select)

    plot_matrix(0); plt.show()


# Функция simple_plot_all_matrices (без изменений)
def simple_plot_all_matrices(value_counts):
    num_matrices = len(value_counts)
    if num_matrices == 0: print("Нет данных."); return
    saved_files = []
    for i, counts in enumerate(value_counts):
        filename = f'matrix_{i+1}_distribution.png'
        try:
            plt.figure(figsize=(10, 6)); ax = plt.gca()
            if not counts:
                ax.text(0.5, 0.5, "Нет данных", ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f'Мат {i+1} (пусто)'); ax.set_xlabel('Значение'); ax.set_ylabel('Частота')
                ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.grid(True, alpha=0.5)
            else:
                items = sorted(counts.items()); values = [x[0] for x in items]; freqs = [x[1] for x in items]
                ax.scatter(values, freqs, s=80, alpha=0.8, color='#007acc', edgecolors='black', linewidth=0.5)
                uniq_f = sorted(list(set(freqs))); max_f = max(freqs) if freqs else 1
                for f in uniq_f: ax.axhline(y=f, color='grey', linestyle=':', alpha=0.5)
                ax.set_xlabel('Значение (искл -1)'); ax.set_ylabel('Частота')
                ax.set_title(f'Распределение в Мат {i+1}'); ax.set_xlim(-0.05, 1.05)
                ax.set_ylim(-max_f * 0.05, max_f * 1.15)
                ints_f = sorted([f for f in uniq_f if f == int(f)])
                if 1 < len(ints_f) <= 10: ax.set_yticks(ints_f)
                else: ax.yaxis.get_major_locator().set_params(integer=True)
                cy = ax.get_ylim(); ax.set_ylim(bottom=max(0, cy[0]))
                ax.grid(True, linestyle='--', alpha=0.5)
                for x, y in zip(values, freqs): ax.text(x, y + max_f * 0.03, f'{y}', ha='center', va='bottom', fontsize=9)
            plt.tight_layout(); plt.savefig(filename); plt.close(); saved_files.append(filename)
        except Exception as e: print(f"Ошибка сохранения мат {i+1}: {e}")
    if saved_files: print("\nСохранено:\n" + "\n".join([f"- {f}" for f in saved_files]))

# Функция main (без изменений)
def main():
    filename = input("Имя файла: ")
    matrices = read_matrices_from_file(filename)
    if matrices is None: return
    value_counts = create_value_counts(matrices)
    while True:
        choice = input("\nРежим (1: интерактив, 2: файлы): ")
        if choice == '1': print("\nИнтерактив..."); create_interactive_plot(value_counts); break
        elif choice == '2': print("\nСохранение..."); simple_plot_all_matrices(value_counts); break
        else: print("Неверно.")

if __name__ == "__main__":
    main()
