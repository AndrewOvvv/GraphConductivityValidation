#include <algorithm>
#include <bits/stdc++.h>
#include <cmath>
#include <cstddef>


class Edge {
private:
    std::pair<int, int> e;
public:
    Edge() {
        this->e = {0, 0};
    }

    Edge(int v) {
        this->e = {v, 0};
    }

    Edge(int v, int u) {
        this->e = {v, u};
    }

    Edge(std::pair<int, int> e) {
        this->e = e;
    }

    int& operator[](const std::size_t idx) {
        if (idx < 0 || 1 < idx) {
            throw "Error - edge indexing: incorrect edge index";
        } else if (idx == 0) {
            return (this->e).first;
        } else {
            return (this->e).second;
        }
    }

    const int& operator[](const std::size_t idx) const {
        if (idx < 0 || 1 < idx) {
            throw "Error - edge indexing: incorrect edge index";
        } else if (idx == 0) {
            return (this->e).first;
        } else {
            return (this->e).second;
        }
    }

    bool operator==(const Edge& other) const {
        return ((this->e).first == (other.e).first && (this->e).second == (other.e).second) || 
               ((this->e).first == (other.e).second && (this->e).second == (other.e).first);
    }

    bool operator!=(const Edge& other) const {
        return !(*this == other);
    }

    bool operator<(const Edge& other) const {
        return ((this->e).first < (other.e).first) || 
               ((this->e).first == (other.e).first && (this->e).second < (other.e).second);
    }
};


template<std::size_t size>
class Graph {
private:
    std::array<std::array<bool, size>, size> m;
public:
    Graph(std::vector<std::vector<bool>> &g) {
        if (int(g.size()) != size) {
            throw "Error - graph contructor: incorrect matrix-argument size";
        }
        for (int i = 0; i < int(g.size()); ++i) {
            if (int(g[i].size()) != size) {
                throw "Error - graph contructor: incorrect matrix-argument size";
            }
        }
        
        // coping matrix to class array
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < size; ++j) {
                (this->m)[i][j] = g[i][j];
            }
        }
    }

    // opertator for SELF
    const std::array<bool, size>& operator[](std::size_t x) {
        if (size <= x) {
            throw "Error - graph subscriptor: incorect index value";
        }
        return m[x];
    }

    const bool& operator[](std::size_t x, std::size_t y) {
        if (size <= x || size <= y) {
            throw "Error - graph subscriptor: incorect index value";
        }
        return m[x][y];
    }

    // logical operators between Graph and Graph
    template<int other_size>
    bool operator==(const Graph<other_size>& other) const {
        if (size == other_size) {
            for (int i = 0; i < size; ++i) {
                for (int j = 0; j < size; ++j) {
                    if (m[i][j] != other.m[i][j]) {
                        return false;
                    }
                }
            } 
            return true;
        }
        return false;
    }

    template<int other_size>
    bool operator!=(const Graph<other_size>& other) const {
        if (size == other_size) {
            for (int i = 0; i < size; ++i) {
                for (int j = 0; j < size; ++j) {
                    if (m[i][j] != other.m[i][j]) {
                        return true;
                    }
                }
            } 
            return false;
        }
        return true;
    }

    // logical operators between Graph and Edge
    template<std::size_t nsize>
    friend bool operator<(const Graph<nsize>& graph, const Edge& edge);

    template<std::size_t nsize>
    friend bool operator>(const Edge& edge, const Graph<nsize>& graph);
    
    // operations between Grah and Edge
    template<std::size_t nsize>
    friend Graph<nsize> operator+(const Graph<nsize>& graph, const Edge& edge); 

    template<std::size_t nsize>
    friend Graph<nsize> operator-(const Graph<nsize>& graph, const Edge& edge);

    template<std::size_t nsize>
    friend Graph<nsize>& operator+=(Graph<nsize>& graph, const Edge& edge);

    template<std::size_t nsize>
    friend Graph<nsize>& operator-=(Graph<nsize>& graph, const Edge& edge);

    // operations with Graph
    void operator!() {
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < size; ++j) {
                (this->m)[i][j] = !(this->m)[i][j];
            }
        }
    }

    // operation between Graph and Graph
    Graph<size> operator+(const Graph<size>& other) {
        Graph<size> new_graph(*this);
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < size; ++j) {
                if (other[i, j]) {
                    new_graph += Edge(i, j);
                }
            }
        }
        return new_graph;
    }

    Graph<size> operator-(const Graph<size>& other) {
        Graph<size> new_graph(*this);
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < size; ++j) {
                if (other[i, j]) {
                    new_graph -= Edge(i, j);
                }
            }
        }
        return new_graph;
    }

    bool operator%(const Graph<size>& other) {
        std::vector<int> permutation(size);
        for (int i = 0; i < size; ++i) {
            permutation[i] = i;
        }

        Graph<size> permutated_graph(*this);

        do {
            // generate new permutated graph
            for (int i = 0; i < size; ++i) {
                for (int j = i; j < size; ++j) {
                    permutated_graph -= {i, j};
                    if ((*this)[i, j]) {
                        permutated_graph += {permutation[i], permutation[j]};
                    }
                }
            }

            // check if permutated graph is equal to other
            if (permutated_graph == other) {
                return true;
            }
        } while (std::next_permutation(permutation.begin(), permutation.end()));
        return false;
    }

    Graph<size>& operator+=(const Graph<size>& other) {
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < size; ++j) {
                if (other[i, j]) {
                    (*this) += Edge(i, j);
                }
            }
        }
        return *this;
    }

    Graph<size>& operator-=(const Graph<size>& other) {
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < size; ++j) {
                if (other[i, j]) {
                    (*this) -= Edge(i, j);
                }
            }
        }
        return *this;
    }
};

template<std::size_t size>
bool operator<(const Graph<size>& graph, const Edge& edge) {
    for (int i = 0; i < 2; ++i) {
        if (edge[i] < 0 || size <= edge[i]) {
            return false;
        }
    }
    return graph[edge[0], edge[1]];
}

template<std::size_t size>
bool operator>(const Edge& edge, const Graph<size>& graph) {
    for (int i = 0; i < 2; ++i) {
        if (edge[i] < 0 || size <= edge[i]) {
            return false;
        }
    }
    return graph[edge[0], edge[1]];
}

template<std::size_t size>
Graph<size> operator+(const Graph<size>& graph, const Edge& edge) {
    Graph<size> new_graph(graph);
    new_graph.m[edge[0]][edge[1]] = true;
    new_graph.m[edge[1]][edge[0]] = true;
    return new_graph;
}

template<std::size_t size>
Graph<size> operator-(const Graph<size>& graph, const Edge& edge) {
    Graph<size> new_graph(graph);
    new_graph.m[edge[0]][edge[1]] = false;
    new_graph.m[edge[1]][edge[0]] = false;
    return new_graph;
}

template<std::size_t size>
Graph<size>& operator+=(Graph<size>& graph, const Edge& edge) {
    graph.m[edge[0]][edge[1]] = true;
    graph.m[edge[1]][edge[0]] = true;
    return graph;
}

template<std::size_t size>
Graph<size>& operator-=(Graph<size>& graph, const Edge& edge) {
    graph.m[edge[0]][edge[1]] = false;
    graph.m[edge[1]][edge[0]] = false;
    return graph;
}

int main() {}
