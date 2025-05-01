import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.special import factorial

# --- Параметры вашего алгоритма ---
n_ref = 100  # Референсное количество вершин
p_ref = 20   # Референсное количество процессов
t_ref_minutes = 20  # Референсное время в минутах
t_ref_seconds = t_ref_minutes * 60  # Референсное время в секундах

# --- Расчет константы для вашего алгоритма ---
# Предполагаем, что работа Work = k * n^12
# Время T = Work / p => Work = T * p
work_ref = t_ref_seconds * p_ref
# k = Work / n^12
# Используем math.pow для больших чисел, преобразуя n_ref в float, чтобы избежать переполнения int
try:
    k_yours = work_ref / math.pow(float(n_ref), 12)
except OverflowError:
    print(f"Ошибка: Вычисление {n_ref}^12 привело к переполнению. Используем приблизительные методы.")
    # Если n_ref очень велико, используем логарифмы или библиотеки для больших чисел
    # Но для n=100 стандартные float могут справиться
    k_yours = work_ref / (float(n_ref)**4)

print(f"Расчетная константа для вашего алгоритма (k_yours): {k_yours:.2e}")

# --- Функция времени для вашего алгоритма (на p_ref процессах) ---
def time_yours(n, k=k_yours, p=p_ref):
  """Оценивает время выполнения вашего алгоритма на p процессах."""
  # Используем np.power для работы с массивами numpy
  # Преобразуем n в float для согласованности и избежания переполнения
  n_float = np.asarray(n, dtype=float)
  try:
      work = np.power(n_float, 5)
      return work / math.sqrt(p)
  except OverflowError:
      # Возвращаем бесконечность при переполнении для больших n
      return np.full_like(n_float, np.inf)

# --- Параметры и функция времени для "Классического" алгоритма ---
# Допущение: Асимптотика O(2^n) (как пример экспоненциального роста)
# Оценим k_classical, предполагая T_yours(n=2, p=10) ≈ T_classical(n=2, p=1)
n_small = 2
time_yours_small = time_yours(n_small)

# T_classical(n) = k_classical * 2^n
# k_classical = T_classical(n=2) / 2^2
# Если время для n=2 слишком мало или не рассчиталось,
# выберем произвольную малую константу, например, 1e-9
# Это повлияет на точку пересечения, но не на форму кривой
print("Предупреждение: Не удалось оценить k_classical из T_yours(2). Используется значение по умолчанию 1e-9.")
k_classical = 1e-9 # Примерное значение - одна операция занимает 1 нс

print(f"Расчетная константа для классического алгоритма (k_classical): {k_classical:.2e}")

def time_classical(n, k=k_classical):
    """
    Оценивает время выполнения алгоритма со сложностью O(n!).
    Использует факториал вместо 2^n.
    """
    try:
        # Преобразуем n в массив NumPy целых чисел,
        # так как факториал определен для неотрицательных целых.
        # Если исходные n - float, они будут усечены.
        # Добавим проверку на отрицательные значения.
        n_int = np.asarray(n, dtype=int)

        if np.any(n_int < 0):
            raise ValueError("Факториал не определен для отрицательных чисел.")
        result = np.zeros_like(n_int, dtype=float)
        result = factorial(n_int, exact=False) / p_ref
        return result
    except ValueError as e:
        print(f"Ошибка входных данных: {e}")
        # Возвращаем массив с NaN или генерируем исключение дальше,
        # в зависимости от желаемого поведения.
        return np.full_like(np.asarray(n), np.nan, dtype=float)
    except TypeError:
        print("Ошибка: Входные данные n должны быть числовыми или массивом чисел.")
        # Возвращаем массив с NaN или генерируем исключение
        # Попытаемся создать массив формы n, если это возможно
        try:
            return np.full_like(np.asarray(n), np.nan, dtype=float)
        except: # Если n совсем некорректный (например, строка)
             raise TypeError("Некорректный тип входных данных n.")

# --- Генерация данных для графика ---
# Выбираем диапазон n. От 2 до 100, чтобы включить референсную точку.
n_values = np.arange(2, 101, 1) # От n=2 до n=100 включительно

# Рассчитываем время для каждого n
times_y = time_yours(n_values)
times_c = time_classical(n_values)

# --- Построение графика ---
plt.figure(figsize=(12, 8))

plt.plot(n_values, times_y, label=f'Алгоритм на проводимостях - O(n^5 / sqrt(p)), где p - кол-во процессов для распараллеливания', linewidth=2)
plt.plot(n_values, times_c, label='Классический алгоритм - O(n! / p), где p - кол-во процессов для распараллеливания', linestyle='--', linewidth=2)

# Настройка графика
plt.xlabel("Количество вершин графа (n)")
plt.ylabel("Асимптотическое кол-во операций")
plt.title("Сравнение асимптотик алгоритмов изоморфизма графов")

# Используем логарифмическую шкалу для оси Y
plt.yscale('log')

# Добавим сетку
plt.grid(True, which="both", linestyle='--', linewidth=0.5)

# Добавим легенду
plt.legend()

# Ограничим ось Y, если значения становятся слишком большими или малыми
min_time = min(np.min(times_y[np.isfinite(times_y)]), np.min(times_c[np.isfinite(times_c)]))
max_time = max(np.max(times_y[np.isfinite(times_y)]), np.max(times_c[np.isfinite(times_c)]))

# Установим разумные пределы, если они существуют и не слишком разбросаны
if min_time > 0 and max_time > min_time and np.isfinite(min_time) and np.isfinite(max_time):
     # Добавим небольшой запас сверху и снизу на лог шкале
     plt.ylim(min_time / 10, max_time * 10)
elif max_time > 0 and np.isfinite(max_time):
     plt.ylim(1e-12, max_time * 10) # Если минимум не определен, ставим маленький


# Показать график
plt.tight_layout() # Чтобы текст не накладывался
plt.show()

# --- Дополнительная информация ---
print("\n--- Пояснения ---")
print(f"1. Ваш алгоритм (O(n^12)) сравнивается с гипотетическим классическим алгоритмом (O(2^n)).")
print(f"2. Время вашего алгоритма показано для {p_ref} процессов, как указано.")
print(f"3. Время классического алгоритма оценено для 1 процесса.")
print(f"4. Константы пропорциональности k оценены на основе точки (n={n_ref}, T={t_ref_minutes} мин, p={p_ref}) и предположения T_yours(2)≈T_class(2).")
print(f"5. График использует логарифмическую шкалу по оси Y из-за огромной разницы во времени выполнения.")
print(f"6. Сложность O(n^12) является чрезвычайно высокой для полиномиального алгоритма. Даже для небольших n время растет очень быстро.")
print(f"7. Это теоретические оценки. Реальная производительность может сильно отличаться из-за структуры графов, реализации, кеширования, накладных расходов на параллелизм и т.д.")

