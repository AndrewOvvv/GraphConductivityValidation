fin = open("double_graph50_res", "r")

n = int(fin.readline())
size = int(fin.readline())

matrix_compressed = dict()
current_matrix, current_line = 0, 0
for line in fin.readlines():
    if len(line) < 10:
        continue
    if current_line == 0:
        matrix_compressed[current_matrix] = dict()

    line_elements = list(map(float, line.split()))
    for element in line_elements:
        if not(element in matrix_compressed[current_matrix]):
            matrix_compressed[current_matrix][element] = 0
        matrix_compressed[current_matrix][element] += 1

    current_line += 1
    if current_line == size:
        current_line = 0
        current_matrix += 1

for matrix in matrix_compressed:
    lst = []
    for value in matrix_compressed[matrix]:
        lst.append((value, matrix_compressed[matrix][value]))
    lst = sorted(lst)
    print(lst)

fin.close()
