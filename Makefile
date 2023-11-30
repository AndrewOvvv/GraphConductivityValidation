PP = g++
CL = clang++
PY = python3
SRC = src

all: clean clang_graph

clang_graph:
	$(CL) $(SRC)/Graph.cpp -std=c++2b -Wall -Werror -O3 -o Graph

gpp_graph:
	$(PP) $(SRC)/Graph.cpp -std=c++2b -Wall -Werror -O3 -o Graph

draw_tree_classes:
	$(PY) $(SRC)/drawGraph.py

clean:
	rm -f Graph
