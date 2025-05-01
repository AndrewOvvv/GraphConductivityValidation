import matplotlib.pyplot as plt
import numpy as np
import sys
from matplotlib.lines import Line2D # Для создания кастомной легенды

# --- Параметры ---
#FILENAME = './test/type_tree/6/graph6_res_func'  # Имя входного файла
FILENAME = './test/type_default/100/graph100_res_func'  # Имя входного файла
VALUES_PER_LINE = 8000  # Ожидаемое количество значений в каждой строке
LINES_PER_GROUP = 30    # Количество строк (графиков), образующих одну группу

# --- Настройка цветов и названий для легенды ---
# Используем стандартную палитру tab10, она хорошо различается
# Вы можете добавить больше цветов и названий, если групп ожидается много
color_values = plt.cm.get_cmap('tab10').colors
color_names = [
    'Синий', 'Оранжевый', 'Зеленый', 'Красный', 'Фиолетовый',
    'Коричневый', 'Розовый', 'Серый', 'Оливковый', 'Бирюзовый'
]
# Убедимся, что у нас достаточно названий для цветов (хотя бы столько, сколько в палитре)
if len(color_names) < len(color_values):
    print(f"Предупреждение: Задано меньше названий ({len(color_names)}), чем цветов в палитре ({len(color_values)}).")
    # Можно дополнить стандартными названиями или оставить как есть

# -------------------

def plot_grouped_data(filename, values_per_line, lines_per_group):
    """
    Читает данные из файла, группирует строки и строит графики.

    Args:
        filename (str): Путь к файлу с данными.
        values_per_line (int): Ожидаемое количество значений в строке.
        lines_per_group (int): Количество строк в одной группе.
    """
    all_data = []
    line_number_global = 0

    print(f"Чтение данных из файла: {filename}")
    try:
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                line_number_global = i + 1
                line = line.strip()
                if not line: # Пропускаем пустые строки
                    continue
                try:
                    # Разбиваем строку по пробелам и преобразуем в числа float
                    values = np.array(list(map(float, line.split())))
                    # Проверяем количество значений
                    if len(values) != values_per_line:
                        print(f"Ошибка в строке {line_number_global}: Ожидалось {values_per_line} значений, найдено {len(values)}. Строка пропущена.", file=sys.stderr)
                        continue
                    all_data.append(values[9000:])
                except ValueError:
                    print(f"Ошибка в строке {line_number_global}: Не удалось преобразовать данные в числа. Строка пропущена.", file=sys.stderr)
                    continue
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден.", file=sys.stderr)
        return
    except Exception as e:
        print(f"Произошла непредвиденная ошибка при чтении файла: {e}", file=sys.stderr)
        return

    if not all_data:
        print("В файле не найдено корректных данных для построения графиков.", file=sys.stderr)
        return

    print(f"Прочитано {len(all_data)} строк с данными.")
    print(f"Построение графиков (группы по {lines_per_group} линий)...")

    fig, ax = plt.subplots(figsize=(12, 6)) # Создаем фигуру и оси

    num_colors = len(color_values)
    group_colors_used = {} # Словарь для хранения цвета для каждой группы {group_index: color_value}

    # Ось X - просто порядковые номера точек (от 0 до N-1)
    x_values = np.arange(len(all_data[0]))

    for line_index, y_values in enumerate(all_data):
        group_index = line_index // lines_per_group
        color_index = group_index % num_colors
        current_color_value = color_values[color_index]

        # Сохраняем цвет группы, если он еще не сохранен (для легенды)
        if group_index not in group_colors_used:
            group_colors_used[group_index] = current_color_value

        # Рисуем линию текущим цветом группы
        ax.plot(x_values, y_values, color=current_color_value, alpha=0.7) # alpha для лучшей видимости при наложении

    # --- Создание кастомной легенды ---
    legend_elements = []
    # Сортируем индексы групп для порядка в легенде
    sorted_group_indices = sorted(group_colors_used.keys())

    for group_index in sorted_group_indices:
        color_value = group_colors_used[group_index]
        color_index = group_index % num_colors
        # Используем название цвета, если оно есть, иначе просто "Цвет X"
        name = color_names[color_index] if color_index < len(color_names) else f"Цвет {color_index + 1}"
        label = f"{name} - Граф №{group_index + 1}"
        legend_elements.append(Line2D([0], [0], color=color_value, lw=3, label=label)) # lw=3 для жирной линии в легенде

    # --- Настройка графика ---
    ax.set_xlabel("Время (дисретные точки во времени)")
    ax.set_ylabel("Вероятность")
    ax.set_title(f"Графики функций провожимости для неизоморфных графов (каждый цвет - отдельный граф)")
    ax.grid(True, linestyle='--', alpha=0.6) # Добавляем сетку

    # Добавляем кастомную легенду
    if legend_elements:
        ax.legend(handles=legend_elements, title="Группы графиков")
    else:
         print("Нет данных для отображения легенды.")

    print("График готов. Отображение...")
    #plt.tight_layout() # Автоматически подгоняет элементы графика, чтобы они не перекрывались
    plt.show()

# --- Запуск ---
if __name__ == "__main__":
    plot_grouped_data(FILENAME, VALUES_PER_LINE, LINES_PER_GROUP)
