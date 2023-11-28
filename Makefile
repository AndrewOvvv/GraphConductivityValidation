PP = g++
CL = clang++
SRC = src

all: clean clang_graph

clang_graph:
	$(CL) $(SRC)/Graph.cpp -std=c++2b -Wall -Werror -O3 -o Graph

gpp_graph:
	$(PP) $(SRC)/Graph.cpp -std=c++2b -Wall -Werror -O3 -o Graph

clean:
	rm -f Graph
