import numpy as np
import matplotlib.pyplot as plt
from sklearn.isotonic import IsotonicRegression
import os
import traceback

# --- Параметры ---
NUM_POINTS = 2000
X_MIN = 0
X_MAX = 500
# Новые параметры для отображаемого диапазона X
X_PLOT_MIN = 480
X_PLOT_MAX = 500
# Имя выходного файла для комбинированного графика
OUTPUT_FILENAME_SINGLE = "plot_{filename}_all_lines_norm_tail.png" # Шаблон для одного файла
OUTPUT_FILENAME_MULTI = "combined_plot_multi_file_norm_tail.png" # Имя для нескольких файлов
OUTPUT_DIR = "plots_output" # Общая папка для итоговых графиков
# -----------------

def read_data_file(filename):
    """
    Читает данные из файла. Ожидает NUM_POINTS float значений в каждой строке.
    Возвращает список numpy массивов (каждый массив - одна строка данных).
    """
    data_lines = []
    line_num = 0
    print(f"Чтение файла: {filename}...")
    try:
        with open(filename, 'r') as f:
            for line in f:
                line_num += 1
                line = line.strip()
                if not line: continue # Пропускаем пустые строки
                try:
                    values = np.array(list(map(float, line.split())))
                    if values.shape[0] != NUM_POINTS:
                        print(f"  Предупреждение: Строка {line_num} в файле '{filename}' содержит {values.shape[0]} значений, ожидалось {NUM_POINTS}. Строка пропущена.")
                        continue
                    data_lines.append(values)
                except ValueError:
                    print(f"  Предупреждение: Строка {line_num} в файле '{filename}' содержит нечисловые данные. Строка пропущена.")
                    continue
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден.")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при чтении файла '{filename}': {e}")
        traceback.print_exc()
        return None

    if not data_lines:
        print(f"В файле '{filename}' не найдено корректных строк данных.")
        return None # Возвращаем None, если данных нет

    print(f"  Файл '{filename}' прочитан, найдено {len(data_lines)} строк данных.")
    return data_lines

def create_monotonic_approximation(x_values, y_values):
    """
    Создает монотонно возрастающую аппроксимацию с помощью изотонической регрессии.
    """
    iso_reg = IsotonicRegression(increasing=True, y_min=0, out_of_bounds='clip')
    y_iso = iso_reg.fit_transform(x_values, y_values)
    return y_iso

def main():
    """
    Основная функция программы.
    Если указан один файл, обрабатывает все его строки и строит на одном графике.
    Если указано несколько файлов, обрабатывает первую строку каждого и строит на одном графике.
    """
    filenames_input = input("Введите имя файла или имена файлов через запятую: ")
    filenames = [name.strip() for name in filenames_input.split(',') if name.strip()]

    if not filenames:
        print("Не указано ни одного имени файла.")
        return

    # --- Создаем общую фигуру и оси для всех графиков ---
    fig, ax = plt.subplots(figsize=(12, 7))
    x_values = np.linspace(X_MIN, X_MAX, NUM_POINTS)
    plot_max_y = 1.05 # Общий верхний предел для оси Y (т.к. нормируем)
    lines_plotted_count = 0
    graph_counter = 0 # --- Счетчик для нумерации графов в легенде ---
    output_filename = "" # Определим позже

    # --- ИНИЦИАЛИЗАЦИЯ ПУТИ ВЫВОДА ---
    output_dir_path = OUTPUT_DIR

    # --- Создаем папку для графиков, если ее нет ---
    if not os.path.exists(OUTPUT_DIR):
        try:
            os.makedirs(OUTPUT_DIR)
            print(f"\nСоздана директория: {OUTPUT_DIR}")
        except OSError as e:
            print(f"Ошибка создания директории {OUTPUT_DIR}: {e}. Графики будут сохранены в текущей директории.")
            output_dir_path = "."
    # else: папка существует, output_dir_path остается OUTPUT_DIR

    # --- Логика в зависимости от количества файлов ---
    if len(filenames) == 1:
        # --- Обработка одного файла (все строки) ---
        filename = filenames[0]
        base_filename = os.path.basename(filename) # Используем для имени файла вывода
        print(f"\nНачинаем обработку одного файла: {filename}")
        all_y_data = read_data_file(filename)

        if all_y_data:
            # Заголовок теперь устанавливается позже, вне if/else
            output_filename = OUTPUT_FILENAME_SINGLE.format(filename=os.path.splitext(base_filename)[0])

            for i, y_original in enumerate(all_y_data):
                print(f"  Обработка строки {i + 1}...")
                y_monotonic = create_monotonic_approximation(x_values, y_original)

                max_y_val = np.max(y_monotonic)
                if max_y_val < 1e-9:
                    y_normalized = y_monotonic
                    print(f"    Предупреждение: Макс. значение в строке {i+1} близко к нулю. Нормировка не применяется.")
                else:
                    y_normalized = y_monotonic / max_y_val

                plot_indices = np.where((x_values >= X_PLOT_MIN) & (x_values <= X_PLOT_MAX))[0]

                if len(plot_indices) == 0:
                    print(f"    Предупреждение: В строке {i+1} нет данных в диапазоне X от {X_PLOT_MIN} до {X_PLOT_MAX}.")
                    continue

                x_plot = x_values[plot_indices]
                y_plot = y_normalized[plot_indices]

                # --- Используем счетчик для легенды ---
                graph_counter += 1
                ax.plot(x_plot, y_plot, '-', linewidth=2, label=f"Граф {graph_counter}")
                lines_plotted_count += 1
        else:
             print(f"Не удалось получить данные из файла '{filename}'. График не будет создан.")

    else:
        # --- Обработка нескольких файлов (первая строка каждого) ---
        print(f"\nНачинаем обработку {len(filenames)} файлов (используется первая строка каждого)...")
        # Заголовок теперь устанавливается позже, вне if/else
        output_filename = OUTPUT_FILENAME_MULTI

        for filename in filenames:
            file_data = read_data_file(filename)
            if file_data is None or not file_data:
                print(f"Пропуск файла '{filename}', т.к. не удалось прочитать данные или файл пуст.")
                continue

            y_original = file_data[0]
            base_filename = os.path.basename(filename) # Не используется для легенды, но полезно для сообщений
            print(f"  Обработка первой строки из файла '{filename}'...")

            y_monotonic = create_monotonic_approximation(x_values, y_original)

            max_y_val = np.max(y_monotonic)
            if max_y_val < 1e-9:
                y_normalized = y_monotonic
                print(f"    Предупреждение: Макс. значение в '{base_filename}' близко к нулю. Нормировка не применяется.")
            else:
                y_normalized = y_monotonic / max_y_val

            plot_indices = np.where((x_values >= X_PLOT_MIN) & (x_values <= X_PLOT_MAX))[0]

            if len(plot_indices) == 0:
                print(f"    Предупреждение: В данных из '{base_filename}' нет точек в диапазоне X от {X_PLOT_MIN} до {X_PLOT_MAX}.")
                continue

            x_plot = x_values[plot_indices]
            y_plot = y_normalized[plot_indices]

            # --- Используем счетчик для легенды ---
            graph_counter += 1
            ax.plot(x_plot, y_plot, '-', linewidth=2, label=f"Граф {graph_counter}")
            lines_plotted_count += 1

    # --- Настройка и сохранение общего графика, если что-то было нарисовано ---
    if lines_plotted_count > 0:
        # --- Установка новых подписей и заголовка ---
        ax.set_title("Сравнение вероятностей") # Общий заголовок
        ax.set_xlim(X_PLOT_MIN, X_PLOT_MAX)
        ax.set_ylim(0, plot_max_y)
        ax.set_xlabel("Время (микросекунды)") # Новая подпись оси X
        ax.set_ylabel("Вероятность") # Новая подпись оси Y
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend() # Добавляем легенду с подписями "Граф 1", "Граф 2"...

        # --- Сохранение графика ---
        if not output_filename:
             print("\nОшибка: Имя выходного файла не было определено. График не сохранен.")
        else:
             output_path = os.path.join(output_dir_path, output_filename)
             try:
                 plt.savefig(output_path)
                 print(f"\nГрафик сохранен: {output_path}")
             except Exception as e:
                 print(f"Не удалось сохранить график {output_path}: {e}")

        plt.show()
        plt.close(fig)

    else:
        print("\nНе было нарисовано ни одной линии (данные отсутствуют или не попадают в диапазон X). График не создан.")
        plt.close(fig) # Закрываем пустую фигуру

    print("\nОбработка завершена.")

if __name__ == "__main__":
    main()
