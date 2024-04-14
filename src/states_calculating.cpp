#include "QComputations_CPU_CLUSTER_NO_PLOTS.hpp"
#include "../include/graph.hpp"
#include <cstddef>
#include <vector>

void READ_n(MPI_File *fin, int *n) {
    MPI_File_read_at_all(*fin, 0, n, 1, MPI_CHAR, MPI_STATUS_IGNORE);
}

void READ_graph(MPI_File *fin, int step, std::vector<std::vector<bool>> &graph) {
    int gsz = graph.size();
    MPI_Offset start_of_graph = 4 + step * (4 + 4 * gsz * gsz) + 4;
    for (int i = 0; i < graph.size(); ++i) {
        for (int j = 0; j < graph.size(); ++i) {
            MPI_File_read_at_all(*fin, start_of_graph, &graph[i][j], 1, MPI_INT, MPI_STATUS_IGNORE);
            start_of_graph += 4;
        }
    }
}

void WRITE_result(MPI_File *fout, int step, int start, int finish, double p, int size) {
    MPI_Offset off = step * (8 * size * size);
    off += 8 * start * size + 8 * finish;

    MPI_File_write_at(*fout, off, &p, 1, MPI_DOUBLE, MPI_STATUS_IGNORE);
}

template<std::size_t size>
double get_conductivity(const graph::Graph<size>& graph, std::size_t start, std::size_t finish) {
    using namespace QComputations;
    std::vector<size_t> grid_atoms(size, 0); // задаёт количество частиц в каждой полости, у нас везде будут 0
    //for (size_t i = 0; i < size; i++){ // size - number of cavities
    //    grid_atoms.emplace_back(0);
    //}

    //std::pair<double, double> gamma = std::make_pair(0.01, 2*M_PI), pair_zero = std::make_pair(0, 0);
    //auto contruct_argument = graph.convert_to_system(gamma, pair_zero);
    //Matrix<std::pair<double, double>> waveguides_parametrs(contruct_argument); // матрица параметров

    CHE_State state(grid_atoms);
    for (size_t i = 0; i < size; i++) {
        for (size_t j = 0; j < size; j++) {
            if (graph(i, j)) {
                state.set_waveguide(i, j, 0.09, 2*M_PI);
            }
        }
    }

    state.set_n(1, start); // в 0 полость помещаем 1 фотон
    state.set_leak_for_cavity(finish, 0.012); // для 2 полости делаем утечки 0.001

    State<CHE_State> init_state(state);
    H_TCH H(init_state);

    //show_basis(H.get_basis());

    auto time_vec = linspace(0, 10000, 10000);
    auto probs = Evolution::quantum_master_equation(init_state.fit_to_basis(H.get_basis()), H, time_vec);

    return probs[probs.n() - 1][time_vec.size() - 1];
}

template<std::size_t size>
std::vector<double> calculate_conductivity(const graph::Graph<size>& graph, int argc, char *argv[], int step, MPI_File *fout) {
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    for (std::size_t start = 0; start < size; ++start) {
        for (std::size_t finish = 0; finish < size; ++finish) {
            if (start != finish && (start + finish) % size == rank) {
                double p = get_basis(graph, start, finish);
                WRITE_result(fout, step, start, finish, p);
            } else if (start == finish && (start + finish) % size == rank) {
                WRITE_result(fout, step, start, finish, -1, graph.size());
            }
        }
    }
    return result;
}

int main(int argc, char *argv[]) {
    const int size = 5;
    graph::Graph<size> graph;

    int rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc < 3) {
        if (!rank) {
            fprintf(stderr, "Not enough arguments (give path to files as argument)\n");
        }
        MPI_Finalize();
        return -1;
    }

    int retcode;
    MPI_File fin, fout;

    retcode = MPI_File_open(MPI_COMM_WORLD, argv[1], MPI_MODE_RDONLY, MPI_INFO_NULL, &fin);
    if (retcode) {
        if (!rank) {
            fprintf(stderr, "Couldn't open file for reading: %s\n", argv[1]);
        }
        MPI_Finalize();
        return -1;
    }

    retcode = MPI_File_open(MPI_COMM_WORLD, argv[2], MPI_MODE_CREATE | MPI_MODE_WRONLY, MPI_INFO_NULL, &fout);
    if (retcode) {
        if (!rank) {
            fprintf(stderr, "Couldn't open file for writing: %s\n", argv[2]);
        }
    }

    int n;
    READ_n(&fin, &n);

    std::vector<std::vector<bool>> g(size, std::vector<bool>(size, false));

    for (int i = 0; i < n; ++i) {
        std::cin >> graph;
        READ_graph(&fin, &g);
        graph = graph<size>(g);

        calculate_conductivity(graph, argc, argv, i, &fout);

        /*
        std::cout << "NEW_GRAPH\n";
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < size; j++) {
                std::cout << result[i * size + j] << " ";
            }
            std::cout << std::endl;
        }
        std::cout << std::endl;
        */
    }

    MPI_File_close(&fin);
    MPI_File_close(&fout);
    MPI_Finalize();
    return 0;
}
