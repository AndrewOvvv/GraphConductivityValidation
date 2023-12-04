#include <vector>
#include <chrono>
#include "graph.hpp"

int main(int argc, char *argv[]) {
    std::vector<int> correct_cnt_tree = {1, 1, 1, 1, 2, 3, 6, 11, 23, 47, 106, 235};
    const int size = 8;

    std::vector<bool> combinations(size * (size - 1) / 2);
    std::vector<std::pair<int, int>> indexes(size * (size - 1) / 2);
    std::fill(combinations.begin(), combinations.begin() + size - 1, true);

    graph::Graph<size> graph;

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

    //std::cout << "Indexes were generated." << std::endl;

    std::vector<graph::Graph<size>> not_ismorfic;
    auto start = std::chrono::high_resolution_clock::now();

    int cnt = 0;

    do {
        if (cnt % 1000000 == 0) {
            std::cout << "Reach step: " << cnt << std::endl;
        }
        for (int i = 0; i < int(combinations.size()); ++i) {
            if (combinations[i]) {
                graph += indexes[i];
            } else {
                graph -= indexes[i];
            }
        }
        if (~graph) {
            bool was_same = false;
            for (int j = 0; j < int(not_ismorfic.size()); ++j) {
                if (graph % not_ismorfic[j]) {
                    was_same = true;
                    break;
                }
            }

            if (!was_same) {
                not_ismorfic.push_back(graph);
            }
            if (correct_cnt_tree[size] == int(not_ismorfic.size())) {
                break;
            }
        }
        ++cnt;
    } while (std::prev_permutation(combinations.begin(), combinations.end()));
    auto stop = std::chrono::high_resolution_clock::now();
    double duration = double((std::chrono::duration_cast<std::chrono::microseconds>(stop - start)).count()) / 1000.0;

    std::cout << not_ismorfic.size() << std::endl;
    for (int i = 0; i < int(not_ismorfic.size()); ++i) {
        std::cout << not_ismorfic[i] << std::endl;
    }
    std::cout << "Execution time: " << duration << " ms." << std::endl;
    return 0;
}
