import matplotlib.pyplot as plt
import numpy as np

def plot_matrix_values(matrices_dict, figsize=(12, 8), save_path=None):
    """
    Строит график распределения значений для нескольких матриц.
    
    Параметры:
    matrices_dict -- словарь, где ключи - номера матриц (от 1 до N),
                    значения - словари {float_значение: количество_встреч}
    figsize -- размер графика (ширина, высота) в дюймах
    save_path -- путь для сохранения графика (если None, график не сохраняется)
    """
    plt.figure(figsize=figsize)
    
    for matrix_num, value_counts in matrices_dict.items():
        # Вычисляем общее количество элементов в матрице
        total_elements = sum(value_counts.values())
        
        if total_elements == 0:
            print(f"Предупреждение: Матрица {matrix_num} не содержит элементов.")
            continue
        
        # Получаем отсортированные значения и их взвешенные частоты
        values = sorted(value_counts.keys())
        weighted_counts = [value_counts[val] / total_elements for val in values]
        
        # Строим линию для текущей матрицы
        plt.plot(values, weighted_counts, marker='o', linestyle='-', 
                 label=f'Матрица предельных проводимостей {matrix_num}')
    
    plt.xlabel('Значения предельных проводимостей в графах')
    plt.ylabel('Количество значений в процентном соотношении')
    plt.title('Распределение значений предельных проводимостей для графов')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"График сохранен по пути: {save_path}")
    
    plt.show()

# Пример использования:
if __name__ == "__main__":
    # Создаем тестовые данные
    sample_data = {
        1: {0.1: 5, 0.2: 10, 0.3: 8, 0.4: 2},        # В матрице 1: значение 0.1 встречается 5 раз и т.д.
        2: {0.15: 4, 0.25: 12, 0.35: 8, 0.45: 6},    # Матрица 2
        3: {0.1: 2, 0.2: 5, 0.3: 10, 0.4: 7, 0.5: 3} # Матрица 3
    }
    
    # Построение графика
    plot_matrix_values(sample_data)

