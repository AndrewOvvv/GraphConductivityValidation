#include <vector>
#include <chrono>
#include "graph.hpp"

const int size = 100;
const int edge_ratio = 15;

int main(int argc, char *argv[]) {
    int seed = 1024;
    int cnt_to_generate = 20;
    auto start = std::chrono::high_resolution_clock::now();

    srand(seed);
    
    std::cout << cnt_to_generate << std::endl;
    for (int i = 0; i < cnt_to_generate; ++i) {
        graph::Graph<size> graph;

        for (int j = 0; j < size; ++j) {
            for (int k = 0; k < size; ++k) {
                if (rand() % edge_ratio < 3) {
                    graph += {j, k};
                }
            }
        }

        //std::cout << size << std::endl;
        std::cout << graph << std::endl;
    }


    auto stop = std::chrono::high_resolution_clock::now();
    double duration = double((std::chrono::duration_cast<std::chrono::microseconds>(stop - start)).count()) / 1000.0;

    std::cerr << "Execution time: " << duration << " ms." << std::endl;
    return 0;
}
