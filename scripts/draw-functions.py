import numpy as np
import matplotlib.pyplot as plt
import os

def plot_data_from_file(file_path, output_dir=None, show_plots=True):
    """
    Считывает данные из файла и создает график для каждой строки.
    
    Параметры:
    file_path (str): Путь к файлу с данными
    output_dir (str): Директория для сохранения графиков (если None, графики не сохраняются)
    show_plots (bool): Показывать ли графики в интерактивном режиме
    """
    # Создаем директорию для сохранения графиков, если нужно
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Генерируем значения по оси X: разделение отрезка [0, 500] на 2000 частей
    x_values = np.linspace(0, 500, 2000)
    
    try:
        # Открываем файл и читаем строки
        with open(file_path, 'r') as file:
            for i, line in enumerate(file):
                # Преобразуем строку в массив float значений
                try:
                    y_values = np.array([float(val) for val in line.strip().split()])
                    
                    # Проверяем, что длина массива соответствует ожидаемой
                    if len(y_values) != 2000:
                        print(f"Предупреждение: строка {i+1} содержит {len(y_values)} значений вместо 2000")
                        if len(y_values) < 2000:
                            # Если значений меньше 2000, используем только соответствующее количество x_values
                            x_values_actual = x_values[:len(y_values)]
                        else:
                            # Если значений больше 2000, обрезаем y_values
                            y_values = y_values[:2000]
                            x_values_actual = x_values
                    else:
                        x_values_actual = x_values
                    
                    # Создаем новый график
                    plt.figure(figsize=(12, 6))
                    plt.plot(x_values_actual, y_values, linewidth=1.5)
                    plt.title(f'График для строки {i+1}')
                    plt.xlabel('Значение (от 0 до 500)')
                    plt.ylabel('Величина')
                    plt.grid(True, linestyle='--', alpha=0.7)
                    
                    # Сохраняем график, если указана директория
                    if output_dir:
                        plt.savefig(os.path.join(output_dir, f'plot_line_{i+1}.png'), dpi=300, bbox_inches='tight')
                    
                    # Показываем график, если нужно
                    if show_plots:
                        plt.show()
                    else:
                        plt.close()
                        
                except ValueError as e:
                    print(f"Ошибка при обработке строки {i+1}: {e}")
                    continue
    
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Пример использования
if __name__ == "__main__":
    # Замените 'data.txt' на путь к вашему файлу
    plot_data_from_file('test/type_default/100/graph100_res_func', output_dir='output_graphs')

