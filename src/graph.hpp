#include <algorithm>
#include <iostream>
#include <cmath>
#include <cstddef>
#include <ostream>
#include <utility>
#include <vector>


namespace graph {
    const int HASH_BASE = 42;

    class Edge {
    private:
        std::pair<std::size_t, std::size_t> e;
    public:
        Edge() {
            this->e = {0, 0};
        }

        Edge(int v) {
            this->e = {std::abs(v), 0};
        }

        Edge(int v, int u) {
            this->e = {std::abs(v), std::abs(u)};
        }

        Edge(std::size_t v, std::size_t u) {
            this->e = {v, u};
        }

        Edge(std::pair<int, int> e) {
            this->e = {std::abs(e.first), std::abs(e.second)};
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

        long double _get_hash(std::size_t current, std::size_t parent,  std::vector<std::vector<std::size_t>> &graph) const {
            long double current_hash = HASH_BASE;
            std::vector<long double> sons_hash;
            for (auto &u : graph[current]) {
                if (u != parent) {
                   sons_hash.push_back(_get_hash(u, current, graph)); 
                }
            }
            std::sort(sons_hash.begin(), sons_hash.end());
            for (auto &hash : sons_hash) {
                current_hash += std::log(hash);
            }
            return current_hash;
        }

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

        const bool& operator()(std::size_t x, std::size_t y) const {
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

        long double get_hash(std::size_t root) const {
            auto self_modified = (*this).convert_to_list();
            return _get_hash(root, root, self_modified);
        }

        std::vector<std::vector<std::size_t>> convert_to_list() const {
            std::vector<std::vector<std::size_t>> new_graph(size);
            for (std::size_t i = 0; i < size; ++i) {
                for (std::size_t j = 0; j < size; ++j) {
                    if ((*this)(i, j)) {
                        new_graph[i].push_back(j);
                    }
                }
            }
            return new_graph;
        }

        std::vector<std::vector<std::pair<double, double>>> convert_to_system(
                                                                            std::pair<double, double> edge, 
                                                                            std::pair<double, double> no_edge) const {
            std::vector<std::vector<std::pair<double, double>>> result(
                                                                        size,
                                                                        std::vector<std::pair<double, double>> (size));
            for (int i = 0; i < size; ++i) {
                for (int j = 0; j < size; ++j) {
                    if ((*this)(i, j)) {
                        result[i][j] = edge;
                    } else {
                        result[i][j] = no_edge;
                    }
                }
            }
            return result;
        }


        // operation between Graph and Graph
        Graph<size> operator+(const Graph<size>& other) {
            Graph<size> new_graph(*this);
            for (std::size_t i = 0; i < size; ++i) {
                for (std::size_t j = 0; j < size; ++j) {
                    if (other(i, j)) {
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
                    if (other(i, j)) {
                        new_graph -= Edge(i, j);
                    }
                }
            }
            return new_graph;
        }

        bool operator%(const Graph<size>& other) {
            long double self_hash = get_hash(0);

            auto other_modified = other.convert_to_list();
            for (std::size_t other_root = 0; other_root < size; ++other_root) {
                if (self_hash == _get_hash(other_root, other_root, other_modified)) {
                    return true;
                }
            }
            return false;
        }

        Graph<size>& operator+=(const Graph<size>& other) {
            for (std::size_t i = 0; i < size; ++i) {
                for (std::size_t j = 0; j < size; ++j) {
                    if (other(i , j)) {
                        (*this) += Edge(i, j);
                    }
                }
            }
            return *this;
        }

        Graph<size>& operator-=(const Graph<size>& other) {
            for (std::size_t i = 0; i < size; ++i) {
                for (std::size_t j = 0; j < size; ++j) {
                    if (other(i, j)) {
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
        return graph(edge[0], edge[1]);
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
        if (size <= edge[0] || size <= edge[1]) {
            throw "Error - graph + edge operator: incorrect edge";
        }
        Graph<size> new_graph(graph);
        new_graph.m[edge[0]][edge[1]] = true;
        new_graph.m[edge[1]][edge[0]] = true;
        return new_graph;
    }

    template<std::size_t size>
    Graph<size> operator-(const Graph<size>& graph, const Edge& edge) {
        if (size <= edge[0] || size <= edge[1]) {
            throw "Error - graph - edge operator: incorrect edge";
        }
        Graph<size> new_graph(graph);
        new_graph.m[edge[0]][edge[1]] = false;
        new_graph.m[edge[1]][edge[0]] = false;
        return new_graph;
    }

    template<std::size_t size>
    Graph<size>& operator+=(Graph<size>& graph, const Edge& edge) {
        if (size <= edge[0] || size <= edge[1]) {
            throw "Error - graph += edge operator: incorrect edge";
        }
        graph.m[edge[0]][edge[1]] = true;
        graph.m[edge[1]][edge[0]] = true;
        return graph;
    }

    template<std::size_t size>
    Graph<size>& operator-=(Graph<size>& graph, const Edge& edge) {
        if (size <= edge[0] || size <= edge[1]) {
            throw "Error - graph -= edge operator: incorrect edge";
        }
        graph.m[edge[0]][edge[1]] = false;
        graph.m[edge[1]][edge[0]] = false;
        return graph;
    }

    template<std::size_t size>
    void dfs(std::size_t vertex, const Graph<size>& graph, std::vector<int>& used) {
        used[vertex] = true;
        for (std::size_t i = 0; i < size; ++i) {
            if (graph(vertex, i) && !used[i]) {
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
                if (graph(i, j)) {
                    os << '1';
                } else {
                    os << '0';
                }
            }
            os << std::endl;
        }
        return os;
    }

    template<std::size_t size>
    std::istream& operator>>(std::istream& is, Graph<size>& graph) {
        int new_size; is >> new_size;
        for (std::size_t i = 0; i < new_size; ++i) {
            for (std::size_t j = 0; j < new_size; ++j) {
                char c; is >> c;
                if (c == '1') {
                    graph += {i, j};
                } else {
                    graph -= {i, j};
                }
            }
        }
        return is;
    }
}
