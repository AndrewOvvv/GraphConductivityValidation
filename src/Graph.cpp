#include <bits/stdc++.h>


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

    Edge(pair<int, int> e) {
        this->e = e;
    }

    int operator[](size_t idx) {
        if (idx < 0 || 1 < idx) {
            return -1;
        } else if (idx == 0) {
            return (this->e).first;
        } else {
            return (this->e).second;
        }
    }

    bool operator==(const Edge& other) const {
        return ((this->e).first == (other->e).first && (this->e).second == (other->e).second) || 
               ((this->e).first == (other->e).second && (this->e).second == (other->e).first);
    }

    bool operator!=(const Edge& other) const {
        return !(*this == other);
    }

    bool operator<(const Edge& other) const {
        return ((this->e).first < (other->e).first) || 
               ((this->e).first == (other->e).first && (this->e).second < (other->e).second);
    }
}


template<int SIZE>
class Graph {
private:
    int n{SIZE};
    std::array<std::array<bool, SIZE>, SIZE> m;
public:
    Graph(std::vector<vector<bool>> &g) {
        if (int(g.size()) != this->n) {
            throw "Error - graph contructor: incorrect matrix-argument size";
            // do something
        }
        for (int i = 0; i < int(g.size()); ++i) {
            if (int(g[i].size()) != this->n) {
                throw "Error - graph contructor: incorrect matrix-argument size";
                // do something
            }
        }

        
        for (int i = 0; i < this->n; ++i) {
            for (int j = 0; j < this->n; ++j) {
                (this->m)[i][j] = g[i][j];
            }
        }
    }

    // opertator for SELF
    const std::array<bool, SIZE>& operator[](std::size_t x) {
        if (x < 0 || this->n <= x) {
            throw "Error - graph subscriptor: incorect index value";
        }
        return m[x];
    }

    const bool& operator[](std::size_t x, std::size_t y) {
        if (x < 0 || this->n <= x || y < 0 || this->n <= y) {
            throw "Error - graph subscriptor: incorect index value";
        }
        return m[x][y];
    }



    // operators between Graph and Edge
    
}
