#include <algorithm>
#include <bits/stdc++.h>
#include <cmath>
#include <cstddef>
#include <ostream>


class Edge {
private:
    std::pair<std::size_t, std::size_t> e;
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

    Edge(std::size_t v, std::size_t u) {
        this->e = {v, u};
    }

    Edge(std::pair<int, int> e) {
        this->e = {e.first, e.second};
    }

    Edge(std::pair<std::size_t, std::size_t> e) {
        this->e = e;
    }


    std::size_t& operator[](const std::size_t idx) {
        if (1 < idx) {
            throw "Error - edge indexing: incorrect edge index";
        } else if (idx == 0) {
            return (this->e).first;
        } else {
            return (this->e).second;
        }
    }

    const std::size_t& operator[](const std::size_t idx) const {
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
    Graph() {
        for (std::size_t i = 0; i < size; ++i) {
            for (std::size_t j = 0; j < size; ++j) {
                (this->m)[i][j] = false;
            }
        }
    }

    Graph(std::vector<std::vector<bool>> &g) {
        if (g.size() != size) {
            throw "Error - graph contructor: incorrect matrix-argument size";
        }
        for (std::size_t i = 0; i < std::size_t(g.size()); ++i) {
            if (g[i].size() != size) {
                throw "Error - graph contructor: incorrect matrix-argument size";
            }
        }
        
        // coping matrix to class array
        for (std::size_t i = 0; i < size; ++i) {
            for (std::size_t j = 0; j < size; ++j) {
                (this->m)[i][j] = g[i][j];
            }
        }
    }

    // opertator for SELF
    const std::array<bool, size>& operator[](std::size_t x) const {
        if (size <= x) {
            throw "Error - graph subscriptor: incorect index value";
        }
        return m[x];
    }

    const bool& operator[](std::size_t x, std::size_t y) const {
        if (size <= x || size <= y) {
            throw "Error - graph subscriptor: incorect index value";
        }
        return m[x][y];
    }

    // logical operators between Graph and Graph
    template<std::size_t other_size>
    bool operator==(const Graph<other_size>& other) const {
        if (size == other_size) {
            for (std::size_t i = 0; i < size; ++i) {
                for (std::size_t j = 0; j < size; ++j) {
                    if (m[i][j] != other.m[i][j]) {
                        return false;
                    }
                }
            } 
            return true;
        }
        return false;
    }

    template<std::size_t other_size>
    bool operator!=(const Graph<other_size>& other) const {
        if (size == other_size) {
            for (std::size_t i = 0; i < size; ++i) {
                for (std::size_t j = 0; j < size; ++j) {
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
        for (std::size_t i = 0; i < size; ++i) {
            for (std::size_t j = 0; j < size; ++j) {
                (this->m)[i][j] = !(this->m)[i][j];
            }
        }
    }

    template<std::size_t nsize>
    friend bool operator~(const Graph<nsize>& graph);

    template<std::size_t nsize>
    friend void dfs(std::size_t vertex, const Graph<nsize>& graph, std::vector<bool>& used);


    // operation between Graph and Graph
    Graph<size> operator+(const Graph<size>& other) {
        Graph<size> new_graph(*this);
        for (std::size_t i = 0; i < size; ++i) {
            for (std::size_t j = 0; j < size; ++j) {
                if (other[i, j]) {
                    new_graph += Edge(i, j);
                }
            }
        }
        return new_graph;
    }

    Graph<size> operator-(const Graph<size>& other) {
        Graph<size> new_graph(*this);
        for (std::size_t i = 0; i < size; ++i) {
            for (std::size_t j = 0; j < size; ++j) {
                if (other[i, j]) {
                    new_graph -= Edge(i, j);
                }
            }
        }
        return new_graph;
    }

    bool operator%(const Graph<size>& other) {
        std::vector<int> permutation(size);
        for (std::size_t i = 0; i < size; ++i) {
            permutation[i] = i;
        }

        Graph<size> permutated_graph(*this);

        do {
            // generate new permutated graph
            for (std::size_t i = 0; i < size; ++i) {
                for (std::size_t j = i; j < size; ++j) {
                    permutated_graph -= {i, j};
                }
            }
            for (std::size_t i = 0; i < size; ++i) {
                for (std::size_t j = i; j < size; ++j) {
                    if ((*this)[i, j]) {
                        permutated_graph += {permutation[i], permutation[j]};
                    }
                }
            }

            /*
            std::cout << permutated_graph << std::endl;
            std::cout << other << std::endl;
            for (std::size_t i = 0; i < size; ++i) {
                std::cout << permutation[i] << " ";
            }
            std::cout << std::endl;
            std::cout << std::endl;
            */

            // check if permutated graph is equal to other
            if (permutated_graph == other) {
               return true;
            }
        } while (std::next_permutation(permutation.begin(), permutation.end()));
        return false;
    }

    Graph<size>& operator+=(const Graph<size>& other) {
        for (std::size_t i = 0; i < size; ++i) {
            for (std::size_t j = 0; j < size; ++j) {
                if (other[i, j]) {
                    (*this) += Edge(i, j);
                }
            }
        }
        return *this;
    }

    Graph<size>& operator-=(const Graph<size>& other) {
        for (std::size_t i = 0; i < size; ++i) {
            for (std::size_t j = 0; j < size; ++j) {
                if (other[i, j]) {
                    (*this) -= Edge(i, j);
                }
            }
        }
        return *this;
    }

    // cout overload
    template<std::size_t nsize>
    friend std::ostream& operator<<(std::ostream& os, const Graph<nsize>& graph);
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

template<std::size_t size>
void dfs(std::size_t vertex, const Graph<size>& graph, std::vector<int>& used) {
    used[vertex] = true;
    for (std::size_t i = 0; i < size; ++i) {
        if (graph[vertex, i] && !used[i]) {
            dfs(i, graph, used);
        }
    }
}

template<std::size_t size>
bool operator~(const Graph<size>& graph) {
    std::vector<int> used(size, false);
    dfs(0, graph, used);
    for (std::size_t i = 0; i < size; ++i) {
        if (!used[i]) {
            return false;
        }
    }
    return true;
}

template<std::size_t size>
std::ostream& operator<<(std::ostream& os, const Graph<size>& graph) {
    os << size << std::endl;
    for (std::size_t i = 0; i < size; ++i) {
        for (std::size_t j = 0; j < size; ++j) {
            if (graph[i, j]) {
                os << '1';
            } else {
                os << '0';
            }
        }
        os << std::endl;
    }
    return os;
}

int main(int argc, char *argv[]) {
    const int size = 8;

    std::vector<bool> combinations(size * (size - 1) / 2);
    std::vector<std::pair<int, int>> indexes(size * (size - 1) / 2);
    std::fill(combinations.begin(), combinations.begin() + size - 1, true);

    Graph<size> graph;

    auto start = std::chrono::high_resolution_clock::now();
    int step = 0;
    int first_v = 0, second_v = 1;
    int curr_size = size - 1;
    for (int i = 0; i < int(indexes.size()); ++i) {
        if (step >= curr_size) {
            first_v++;
            second_v = first_v + 1;
            curr_size--;
            step = 0;
        }

        indexes[i] = {first_v, second_v};

        second_v++;
        step++;
    }

    std::cout << "Indexes were generated." << std::endl;

    std::vector<Graph<size>> all_trees;
    do {
        for (int i = 0; i < int(combinations.size()); ++i) {
            if (combinations[i]) {
                graph += indexes[i];
            } else {
                graph -= indexes[i];
            }
        }
        if (~graph) {
            all_trees.push_back(graph);
        }
    } while (std::prev_permutation(combinations.begin(), combinations.end()));
    
    std::cout << "All trees were generated." << std::endl;
    std::cout << "Number of trees: " << all_trees.size() << std::endl;

    std::vector<Graph<size>> not_ismorfic;
    for (int i = 0; i < int(all_trees.size()); ++i) {
        //std::cout << i << "/" << int(all_trees.size()) << "; non-isomorfic: " << int(not_ismorfic.size()) << std::endl;
        bool was_same = false;
        for (int j = 0; j < int(not_ismorfic.size()); ++j) {
            if (all_trees[i] % not_ismorfic[j]) {
                was_same = true;
                //std::cout << i << " " << j << std::endl;
                break;
            }
        }

        if (!was_same) {
            not_ismorfic.push_back(all_trees[i]);
        }
    }
    auto stop = std::chrono::high_resolution_clock::now();
    double duration = double((std::chrono::duration_cast<std::chrono::microseconds>(stop - start)).count()) / 1000.0;
    std::cout << "Non-isomorfic trees were found." << std::endl;

    /*
    std::cout << all_trees.size() << std::endl;
    for (int i = 0; i < int(all_trees.size()); ++i) {
        std::cout << all_trees[i] << std::endl << std::endl;
    }
    */
 
    //std::cout << all_trees[1] % all_trees[2] << std::endl;

    std::cout << not_ismorfic.size() << std::endl;
    for (int i = 0; i < int(not_ismorfic.size()); ++i) {
        std::cout << not_ismorfic[i] << std::endl << std::endl;
    }
    std::cout << "Execution time: " << duration << " ms." << std::endl;
    return 0;
}
