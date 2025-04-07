import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.widgets import RadioButtons
import traceback
import math

# --- Функции read_matrices_from_file и create_value_counts ---
# (Без изменений, как в предыдущем ответе)
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


# --- Интерактивный график с НОРМАЛИЗАЦИЕЙ ---
def create_interactive_plot(value_counts):
    num_matrices = len(value_counts)
    if num_matrices == 0: print("Нет данных для отображения."); return

    max_cols = 6; num_cols = min(num_matrices, max_cols)
    num_rows = math.ceil(num_matrices / num_cols)
    row_height = 0.07
    widget_height = num_rows * row_height + 0.02
    bottom_margin = 0.1 + widget_height

    fig, ax = plt.subplots(figsize=(10, 7 + num_rows * 0.2))
    fig.subplots_adjust(bottom=bottom_margin + 0.03)
    rax = fig.add_axes([0.05, 0.05, 0.9, widget_height])
    rax.set_facecolor('#f0f0f0')
    rax.set_xticks([]); rax.set_yticks([])
    for spine in rax.spines.values(): spine.set_visible(False)

    def plot_matrix(matrix_idx):
        ax.clear()
        counts = value_counts[matrix_idx]
        if not counts:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center', fontsize=12, transform=ax.transAxes)
            ax.set_title(f'Матрица {matrix_idx+1} (нет данных)', fontsize=14)
            ax.set_xlabel('Значение'); ax.set_ylabel('Норм. частота')
            ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.grid(True, linestyle='--', alpha=0.6)
            fig.canvas.draw_idle(); return

        sorted_items = sorted(counts.items())
        values = [item[0] for item in sorted_items]
        original_frequencies = [item[1] for item in sorted_items]

        max_freq_val = max(original_frequencies) if original_frequencies else 1
        if max_freq_val == 0: max_freq_val = 1
        normalized_frequencies = [f / max_freq_val for f in original_frequencies]

        ax.scatter(values, normalized_frequencies, s=80, alpha=0.8, color='#007acc', edgecolors='black', linewidth=0.5)

        unique_norm_freqs = sorted(list(set(normalized_frequencies)))
        for freq_norm in unique_norm_freqs:
            ax.axhline(y=freq_norm, color='grey', linestyle=':', alpha=0.5, linewidth=1)

        ax.set_xlabel('Значение элемента матрицы (исключая -1)', fontsize=11)
        ax.set_ylabel('Нормированная частота', fontsize=11)
        ax.set_title(f'Распределение значений в Матрице {matrix_idx+1} (Норм.)', fontsize=14, pad=10)
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.1)
        ax.set_yticks(np.linspace(0, 1, 6))
        ax.grid(True, linestyle='--', alpha=0.5)

        for x, y_orig, y_norm in zip(values, original_frequencies, normalized_frequencies):
            ax.text(x, y_norm + 0.03, f'{y_orig}',
                    ha='center', va='bottom', fontsize=9)
        fig.canvas.draw_idle()

    labels = [f'Матрица {i+1}' for i in range(num_matrices)]
    radio = RadioButtons(rax, labels, active=0, activecolor='#007acc')

    button_props = []; label_props = []
    hoffset = 0.02; voffset = 0.05
    col_width = (1.0 - 2 * hoffset) / num_cols
    row_height_actual = (1.0 - 2 * voffset) / num_rows
    circle_radius = 0.45 * min(col_width / 3, row_height_actual / 2)
    label_fontsize = 10
    current_row = num_rows - 1; current_col = 0
    for i in range(num_matrices):
        x_center = hoffset + current_col * col_width + col_width / 2
        y_center = voffset + current_row * row_height_actual + row_height_actual / 2
        button_props.append((x_center, y_center))
        x_label = x_center
        y_label = y_center - circle_radius * 3.0
        label_props.append((x_label, y_label))
        current_col += 1
        if current_col >= num_cols: current_col = 0; current_row -= 1

    for i, (circle, label) in enumerate(zip(radio.circles, radio.labels)):
        circle.center = button_props[i]; circle.set_radius(circle_radius)
        circle.set_linewidth(1.5)
        label.set_position(label_props[i]); label.set_fontsize(label_fontsize)
        label.set_horizontalalignment('center'); label.set_verticalalignment('top')

    def matrix_select(label):
        matrix_idx = labels.index(label); plot_matrix(matrix_idx)

    radio.on_clicked(matrix_select)
    plot_matrix(0); plt.show()


# --- НЕинтерактивный график с НОРМАЛИЗАЦИЕЙ ---
def simple_plot_all_matrices(value_counts):
    num_matrices = len(value_counts)
    if num_matrices == 0: print("Нет данных."); return
    saved_files = []
    for i, counts in enumerate(value_counts):
        filename = f'matrix_{i+1}_distribution_normalized.png'
        try:
            plt.figure(figsize=(10, 6)); ax = plt.gca()
            if not counts:
                ax.text(0.5, 0.5, "Нет данных", ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f'Мат {i+1} (пусто)'); ax.set_xlabel('Значение'); ax.set_ylabel('Норм. частота')
                ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.grid(True, alpha=0.5)
            else:
                sorted_items = sorted(counts.items())
                values = [item[0] for item in sorted_items]
                original_frequencies = [item[1] for item in sorted_items]

                max_freq_val = max(original_frequencies) if original_frequencies else 1
                if max_freq_val == 0: max_freq_val = 1
                normalized_frequencies = [f / max_freq_val for f in original_frequencies]

                ax.scatter(values, normalized_frequencies, s=80, alpha=0.8, color='#007acc', edgecolors='black', linewidth=0.5)
                unique_norm_freqs = sorted(list(set(normalized_frequencies)))
                for f_norm in unique_norm_freqs: ax.axhline(y=f_norm, color='grey', linestyle=':', alpha=0.5)
                ax.set_xlabel('Значение элемента матрицы (исключая -1)'); ax.set_ylabel('Нормированная частота')
                ax.set_title(f'Распределение в Мат {i+1} (Норм.)'); ax.set_xlim(-0.05, 1.05)
                ax.set_ylim(-0.05, 1.1); ax.set_yticks(np.linspace(0, 1, 6))
                ax.grid(True, linestyle='--', alpha=0.5)

                for x, y_orig, y_norm in zip(values, original_frequencies, normalized_frequencies):
                     ax.text(x, y_norm + 0.03, f'{y_orig}', ha='center', va='bottom', fontsize=9)

            plt.tight_layout(); plt.savefig(filename); plt.close(); saved_files.append(filename)
        except Exception as e: print(f"Ошибка сохранения норм. мат {i+1}: {e}")
    if saved_files: print("\nСохранено (нормированные):\n" + "\n".join([f"- {f}" for f in saved_files]))


# --- Функция сравнения словарей ---
def compare_value_counts_and_print(value_counts):
    """Сравнивает словари в списке и выводит результат."""
    print("\n--- Сравнение словарей распределений ---")
    num_matrices = len(value_counts)
    if num_matrices <= 1:
        print("Для сравнения необходимо как минимум две матрицы.")
        print("-----------------------------------------\n")
        return

    checked_indices = set() # Индексы матриц, уже вошедших в какую-либо группу
    identical_groups = [] # Список групп, где каждая группа - это set с индексами (1-based)

    for i in range(num_matrices):
        if i in checked_indices:
            continue # Эту матрицу уже сравнивали и нашли ей идентичную

        current_group = {i + 1} # Начинаем новую группу (1-based index)
        is_unique_so_far = True

        # Сравниваем с последующими матрицами
        for j in range(i + 1, num_matrices):
            if j in checked_indices:
                continue # Эта матрица уже в другой группе

            # Сравниваем словари
            if value_counts[i] == value_counts[j]:
                current_group.add(j + 1)
                checked_indices.add(j) # Помечаем j как проверенную
                is_unique_so_far = False

        # Если для i нашлись идентичные, добавляем группу
        if not is_unique_so_far:
            identical_groups.append(current_group)
            checked_indices.add(i) # Помечаем i как вошедшую в группу

    # Вывод результата
    if identical_groups:
        print("Найдены группы идентичных словарей распределений:")
        # Сортируем группы по первому элементу для упорядоченного вывода
        sorted_groups = sorted(identical_groups, key=lambda g: min(g))
        for idx, group in enumerate(sorted_groups):
            # Сортируем индексы внутри группы для красивого вывода
            print(f"  Группа {idx + 1}: Матрицы {sorted(list(group))}")
    else:
        print("Все словари распределений уникальны.")

    print("-----------------------------------------\n")


# --- Основная функция ---
def main():
    filename = input("Имя файла: ")
    matrices = read_matrices_from_file(filename)
    if matrices is None: return

    value_counts = create_value_counts(matrices)

    # Вызываем функцию сравнения ПЕРЕД выбором режима отображения
    compare_value_counts_and_print(value_counts)

    # Выбор режима отображения
    while True:
        choice = input("Выберите режим отображения:\n"
                       "1: Интерактивный график (все матрицы)\n"
                       "2: Сохранить графики в отдельные файлы\n"
                       "Введите 1 или 2: ")
        if choice == '1':
            print("\nЗапуск интерактивного графика...")
            create_interactive_plot(value_counts)
            break
        elif choice == '2':
            print("\nСоздание и сохранение отдельных графиков...")
            simple_plot_all_matrices(value_counts)
            break
        else:
            print("Неверный ввод. Пожалуйста, введите 1 или 2.")


if __name__ == "__main__":
    main()
