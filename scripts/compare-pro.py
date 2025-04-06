import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from scipy.stats import wasserstein_distance
from scipy.spatial.distance import cosine
from sklearn.metrics import mutual_info_score
import pandas as pd

def read_matrices_from_file(filename):
    """Чтение матриц из файла"""
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    
    num_matrices = int(lines[0])
    matrix_size = int(lines[1])
    
    matrices = []
    line_index = 2
    
    for i in range(num_matrices):
        current_matrix = []
        for j in range(matrix_size):
            row = list(map(float, lines[line_index].split()))
            current_matrix.append(row)
            line_index += 1
        
        matrices.append(np.array(current_matrix))
        
        # Пропускаем пустую строку между матрицами, если это не последняя матрица
        if i < num_matrices - 1 and line_index < len(lines):
            line_index += 1
    
    return matrices

def create_value_counts(matrices):
    """Создание словарей с подсчетом значений для каждой матрицы"""
    value_counts = []
    for matrix in matrices:
        # Преобразуем матрицу в одномерный массив и считаем частоты
        counts = dict(Counter(matrix.flatten()))
        value_counts.append(counts)
    
    return value_counts

def plot_histograms(value_counts, matrices):
    """Построение гистограмм распределения значений для каждой матрицы"""
    num_matrices = len(value_counts)
    fig, axes = plt.subplots(1, num_matrices, figsize=(5*num_matrices, 5))
    
    if num_matrices == 1:
        axes = [axes]
    
    for i, (counts, matrix) in enumerate(zip(value_counts, matrices)):
        # Находим все уникальные значения во всех матрицах
        unique_values = sorted(counts.keys())
        frequencies = [counts.get(val, 0) for val in unique_values]
        
        bars = axes[i].bar(range(len(unique_values)), frequencies)
        axes[i].set_xticks(range(len(unique_values)))
        axes[i].set_xticklabels([f"{v:.3f}" for v in unique_values], rotation=45)
        axes[i].set_title(f'Матрица {i+1}')
        axes[i].set_xlabel('Значение')
        axes[i].set_ylabel('Частота')
        
        # Добавляем статистики для матрицы
        stats_text = (f'Среднее: {np.mean(matrix):.4f}\n'
                     f'Ст. откл.: {np.std(matrix):.4f}\n'
                     f'Мин: {np.min(matrix):.4f}\n'
                     f'Макс: {np.max(matrix):.4f}')
        axes[i].text(0.05, 0.95, stats_text, transform=axes[i].transAxes, 
                     verticalalignment='top', bbox=dict(boxstyle='round', alpha=0.1))
    
    plt.tight_layout()
    plt.savefig('histograms.png')
    plt.show()

def plot_combined_histogram(value_counts, matrices):
    """Построение комбинированной гистограммы для всех матриц"""
    plt.figure(figsize=(12, 6))
    
    # Находим все уникальные значения во всех матрицах
    all_values = set()
    for counts in value_counts:
        all_values.update(counts.keys())
    
    unique_values = sorted(all_values)
    
    # Создаем данные для групповой гистограммы
    bar_width = 0.8 / len(matrices)
    
    for i, counts in enumerate(value_counts):
        x_positions = [j + i * bar_width - 0.4 + bar_width/2 for j in range(len(unique_values))]
        frequencies = [counts.get(val, 0) for val in unique_values]
        
        plt.bar(x_positions, frequencies, width=bar_width, 
                label=f'Матрица {i+1}', alpha=0.7)
    
    plt.xticks(range(len(unique_values)), [f"{v:.3f}" for v in unique_values], rotation=45)
    plt.xlabel('Значение')
    plt.ylabel('Частота')
    plt.title('Сравнение распределений значений в матрицах')
    plt.legend()
    plt.tight_layout()
    plt.savefig('combined_histogram.png')
    plt.show()

def plot_cumulative_distributions(matrices):
    """Построение кумулятивных функций распределения"""
    plt.figure(figsize=(10, 6))
    
    for i, matrix in enumerate(matrices):
        # Сортируем значения
        sorted_values = np.sort(matrix.flatten())
        
        # Строим кумулятивное распределение
        y = np.arange(1, len(sorted_values) + 1) / len(sorted_values)
        
        plt.plot(sorted_values, y, label=f'Матрица {i+1}')
    
    plt.xlabel('Значение')
    plt.ylabel('Кумулятивная вероятность')
    plt.title('Функции кумулятивного распределения')
    plt.legend()
    plt.grid(True)
    plt.savefig('cumulative_distributions.png')
    plt.show()

def calculate_similarity_matrix(matrices):
    """Расчет матрицы сходства между матрицами"""
    num_matrices = len(matrices)
    similarity_matrix = np.zeros((num_matrices, num_matrices))
    
    for i in range(num_matrices):
        for j in range(num_matrices):
            # Преобразуем матрицы в одномерные массивы
            flat_i = matrices[i].flatten()
            flat_j = matrices[j].flatten()
            
            # Расчет расстояния Васерштейна (EMD)
            # Меньше значение - более похожие распределения
            distance = wasserstein_distance(flat_i, flat_j)
            similarity = 1.0 / (1.0 + distance)  # Преобразуем в сходство
            similarity_matrix[i, j] = similarity
    
    return similarity_matrix

def plot_similarity_heatmap(similarity_matrix):
    """Визуализация матрицы сходства"""
    plt.figure(figsize=(8, 6))
    
    # Используем красно-синюю цветовую карту, где синий = похожи, красный = различны
    sns.heatmap(similarity_matrix, annot=True, fmt=".3f", cmap='coolwarm',
                xticklabels=[f'Матрица {i+1}' for i in range(similarity_matrix.shape[0])],
                yticklabels=[f'Матрица {i+1}' for i in range(similarity_matrix.shape[0])])
    
    plt.title('Матрица сходства (значения ближе к 1 = более похожи)')
    plt.tight_layout()
    plt.savefig('similarity_heatmap.png')
    plt.show()

def plot_boxplots(matrices):
    """Построение диаграмм ящик с усами для сравнения распределений"""
    plt.figure(figsize=(10, 6))
    
    data = [matrix.flatten() for matrix in matrices]
    labels = [f'Матрица {i+1}' for i in range(len(matrices))]
    
    plt.boxplot(data, labels=labels, patch_artist=True)
    plt.ylabel('Значение')
    plt.title('Сравнение распределений значений в матрицах')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig('boxplots.png')
    plt.show()

def main():
    filename = input("Введите имя файла с матрицами: ")
    
    try:
        # Чтение матриц из файла
        matrices = read_matrices_from_file(filename)
        
        # Создание словарей подсчета значений
        value_counts = create_value_counts(matrices)
        
        # Вывод словарей
        for i, counts in enumerate(value_counts):
            print(f"\nСловарь для матрицы {i+1}:")
            for value, count in sorted(counts.items()):
                print(f"  {value}: {count}")
        
        # Визуализация
        print("\nСоздание визуализаций для сравнения матриц...")
        
        plot_histograms(value_counts, matrices)
        plot_combined_histogram(value_counts, matrices)
        plot_cumulative_distributions(matrices)
        plot_boxplots(matrices)
        
        similarity_matrix = calculate_similarity_matrix(matrices)
        plot_similarity_heatmap(similarity_matrix)
        
        print("\nАнализ завершен. Все графики сохранены в текущей директории.")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()

