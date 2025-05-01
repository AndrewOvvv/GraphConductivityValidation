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
# -----------------

def read_data_file(filename):
    """
    Читает данные из файла. Ожидает NUM_POINTS float значений в каждой строке.
    Возвращает список numpy массивов (каждый массив - одна строка данных).
    """
    data_lines = []
    line_num = 0
    try:
        with open(filename, 'r') as f:
            for line in f:
                line_num += 1
                line = line.strip()
                if not line: continue # Пропускаем пустые строки
                try:
                    values = np.array(list(map(float, line.split())))
                    if values.shape[0] != NUM_POINTS:
                        print(f"Предупреждение: Строка {line_num} содержит {values.shape[0]} значений, ожидалось {NUM_POINTS}. Строка пропущена.")
                        continue
                    data_lines.append(values)
                except ValueError:
                    print(f"Предупреждение: Строка {line_num} содержит нечисловые данные. Строка пропущена.")
                    continue
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден.")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при чтении файла: {e}")
        traceback.print_exc()
        return None

    if not data_lines:
        print("В файле не найдено корректных строк данных.")
        return None

    return data_lines

def create_monotonic_approximation(x_values, y_values):
    """
    Создает монотонно возрастающую аппроксимацию с помощью изотонической регрессии.
    """
    iso_reg = IsotonicRegression(increasing=True, y_min=0, out_of_bounds='clip')
    y_iso = iso_reg.fit_transform(x_values, y_values)
    return y_iso

def plot_and_save_line(x_values, y_monotonic, line_index, output_dir="plots_normalized_tail"):
    """
    Рисует нормированный график монотонной аппроксимации для одной строки
    в диапазоне X_PLOT_MIN до X_PLOT_MAX и сохраняет его в файл.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # --- Нормализация Y ---
    max_y_val = np.max(y_monotonic)
    # Избегаем деления на ноль или очень малые значения, если аппроксимация почти нулевая
    if max_y_val < 1e-9:
        y_normalized = y_monotonic # Оставляем как есть (практически нули)
        plot_max_y = 1 # Для оси Y
        print(f"  Предупреждение: Максимальное значение в строке {line_index+1} близко к нулю. Нормировка не применяется.")
    else:
        y_normalized = y_monotonic / max_y_val
        plot_max_y = 1.05 # Устанавливаем верхний предел оси Y чуть выше 1

    # --- Фильтрация данных для отображения нужного диапазона X ---
    # Находим индексы, соответствующие диапазону X_PLOT_MIN, X_PLOT_MAX
    plot_indices = np.where((x_values >= X_PLOT_MIN) & (x_values <= X_PLOT_MAX))[0]

    if len(plot_indices) == 0:
        print(f"Предупреждение: В строке {line_index+1} нет данных в диапазоне X от {X_PLOT_MIN} до {X_PLOT_MAX}.")
        # Отобразим пустой график с нужными осями
        ax.set_xlim(X_PLOT_MIN, X_PLOT_MAX)
        ax.set_ylim(0, plot_max_y) # Используем рассчитанный plot_max_y
        ax.set_title(f"Строка {line_index + 1}")
    else:
        # Выбираем нужные участки X и Y (нормированного)
        x_plot = x_values[plot_indices]
        y_plot = y_normalized[plot_indices]

        # Рисуем только монотонную нормированную аппроксимацию
        ax.plot(x_plot, y_plot, '-', color='red', linewidth=2, label='Монотонная аппроксимация (норм.)')

        # Настройка пределов осей
        ax.set_xlim(X_PLOT_MIN, X_PLOT_MAX)
        ax.set_ylim(0, plot_max_y) # Ось Y от 0 до 1 (или чуть выше)

        # Добавляем информацию о максимальном значении до нормализации в заголовок
        ax.set_title(f"Строка {line_index + 1}")


    # Общие настройки графика
    ax.set_xlabel(f"X (участок от {X_PLOT_MIN} до {X_PLOT_MAX})")
    ax.set_ylabel("Значение вероятности")
    ax.grid(True, linestyle='--', alpha=0.7)
    # ax.legend() # Легенда не нужна, т.к. рисуем только одну линию

    # Создаем папку для графиков, если ее нет
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Создана директория: {output_dir}")
        except OSError as e:
            print(f"Ошибка создания директории {output_dir}: {e}")
            output_dir = "." # Сохраняем в текущую

    # Сохранение графика
    filename = os.path.join(output_dir, f"line_{line_index + 1:03d}_norm_tail_plot.png")
    try:
        plt.savefig(filename)
        print(f"График сохранен: {filename}")
    except Exception as e:
        print(f"Не удалось сохранить график {filename}: {e}")

    plt.close(fig) # Закрываем фигуру

def main():
    """
    Основная функция программы.
    """
    filename = input("Введите имя файла с данными: ")

    all_y_data = read_data_file(filename)
    if all_y_data is None:
        return

    x_values = np.linspace(X_MIN, X_MAX, NUM_POINTS)

    print(f"\nНачинаем обработку {len(all_y_data)} строк данных...")
    output_dir_name = "plots_normalized_tail" # Имя папки для вывода

    for i, y_original in enumerate(all_y_data):
        print(f"  Обработка строки {i + 1}...")
        # Создаем монотонную аппроксимацию (на всех данных!)
        y_monotonic = create_monotonic_approximation(x_values, y_original)
        # Рисуем и сохраняем НОРМИРОВАННЫЙ УЧАСТОК графика
        plot_and_save_line(x_values, y_monotonic, i, output_dir=output_dir_name)

    print(f"\nОбработка завершена. Графики сохранены в папку '{output_dir_name}'.")

if __name__ == "__main__":
    main()
