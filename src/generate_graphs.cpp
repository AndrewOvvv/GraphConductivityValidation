#include <vector>
#include <chrono>
#include "graph.hpp"

const int size = 100;

int main(int argc, char *argv[]) {
    graph::Graph<size> graph;
    int group_size = 25;
    int group_cnt = size / group_size;

    // get start generation time
    auto start = std::chrono::high_resolution_clock::now();

    // in-groups connection generation
    for (int i = 0; i < group_size; ++i) {
        for (int j = 0; j < group_cnt; ++j) {
            graph += {j * group_size + i, j * group_size + ((i + 1) % group_size)};
        }
    }

    // inter-group connections
    for (int i = 0; i < group_cnt; ++i) {
        for (int j = 0; j < group_cnt; ++j) {
            if (i != j) {
                graph += {i * group_size, j * group_size};
            }
        }
    }

    for (int i = 0; i < group_cnt; ++i) {
        int cgroup = i;
        int ngroup = (i + 1) % group_cnt;
        graph += {cgroup * group_size + 1, ngroup * group_size + (group_size - 2)};
    }

    // get finish generation time
    auto stop = std::chrono::high_resolution_clock::now();
    // get duration of graph generation
    double duration = double((std::chrono::duration_cast<std::chrono::microseconds>(stop - start)).count()) / 1000.0;

    std::cout << graph << std::endl;
    std::cout << "Execution time: " << duration << " ms." << std::endl;
    return 0;
}
