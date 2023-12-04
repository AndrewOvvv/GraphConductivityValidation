CL = clang++
PY = python3

SRC = src
SCRPT = scripts
INCLUDE = include

all: clean generate_graphs

generate_graphs:
	$(CL) $(SRC)/generate_graphs.cpp -I $(INCLUDE) -std=c++2b -Wall -Werror -O3 -o generate_graphs

draw_tree_classes:
	$(PY) $(SCRPT)/drawGraph.py

clean:
	rm -f generate_graphs
