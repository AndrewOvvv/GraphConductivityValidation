import networkx as nx
import matplotlib.pyplot as plt


# startup only with 'make' draw_tree_classes option


# !!!! EDIT ONLY HERE
start_file = 5
finish_file = 10
scaling = 4
# !!!! EDIT ONLY HERE

for file in range(start_file, finish_file + 1):
    print("draw: graph" + str(file))
    fin = open("generated/graph" + str(file), "r")

    cnt = int(fin.readline())
    print(cnt)

    rows = int(cnt ** 0.5)
    rows += 1

    cols = int(cnt ** 0.5)
    cols += 1

    fig = plt.figure(figsize=(scaling * rows, scaling * cols))

    for gr in range(cnt):
        print("step:", gr)
        s = ''
        while len(s) == 0:
            s = fin.readline().rstrip()
        n = int(s.rstrip())
        G = nx.Graph()
        G.add_nodes_from([i for i in range(n)])

        for i in range(n):
            current = fin.readline()
            for j in range(i, n):
                if current[j] == '1':
                    G.add_edge(i, j)
        subax = plt.subplot(rows, cols, gr + 1)
        nx.draw(G)

    plt.savefig("images/tree" + str(file) + ".png")
    fin.close()
