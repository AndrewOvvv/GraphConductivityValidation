#include "QComputations_CPU_CLUSTER_NO_PLOTS.hpp"
//#include "QComputations_SINGLE_NO_PLOTS.hpp"
#include <cstddef>
#include <vector>

void READ_n(MPI_File *fin, int *n) {
    //MPI_File_read_at_all(*fin, 0, n, 1, MPI_INT, MPI_STATUS_IGNORE);
    MPI_File_read(*fin, n, 1, MPI_INT, MPI_STATUS_IGNORE);
}

void READ_graph(MPI_File *fin, int step, std::vector<std::vector<bool>> &graph) {
    int gsz = graph.size();
    MPI_Offset start_of_graph = 4 + step * (4 + 4 * gsz * gsz) + 4;
    for (int i = 0; i < graph.size(); ++i) {
        for (int j = 0; j < graph.size(); ++j) {
            int num;
            MPI_File_read_at(*fin, start_of_graph, &num, 1, MPI_INT, MPI_STATUS_IGNORE);
            graph[i][j] = num;   
            start_of_graph += 4;
        }
    }
}

void WRITE_n(MPI_File *fout, int n, int size) {
    MPI_File_write_at(*fout, 0, &n, 1, MPI_INT, MPI_STATUS_IGNORE);
    MPI_File_write_at(*fout, 4, &size, 1, MPI_INT, MPI_STATUS_IGNORE);
}

void WRITE_result(MPI_File *fout, int step, int start, int finish, double p, int size) {
    MPI_Offset off = 8 + step * (8 * size * size) + 8 * start * size + 8 * finish;;

    MPI_File_write_at(*fout, off, &p, 1, MPI_DOUBLE, MPI_STATUS_IGNORE);
}

template<std::size_t size>
double get_conductivity(const std::vector<std::vector<bool>>& graph, std::size_t start, std::size_t finish) {
    using namespace QComputations;
    std::vector<size_t> grid_atoms(size, 0); // задаёт количество частиц в каждой полости, у нас везде будут 0
    //for (size_t i = 0; i < size; i++){ // size - number of cavities
    //    grid_atoms.emplace_back(0);
    //}

    //std::pair<double, double> gamma = std::make_pair(0.01, 2*M_PI), pair_zero = std::make_pair(0, 0);
    //auto contruct_argument = graph.convert_to_system(gamma, pair_zero);
    //Matrix<std::pair<double, double>> waveguides_parametrs(contruct_argument); // матрица параметров

    TCH_State state(grid_atoms);
    for (size_t i = 0; i < size; i++) {
        for (size_t j = 0; j < size; j++) {
            if (graph[i][j]) {
                state.set_waveguide(i, j, 0.09, 2*M_PI);
            }
        }
    }

    state.set_n(1, start); // в 0 полость помещаем 1 фотон
    state.set_leak_for_cavity(finish, 0.012); // для 2 полости делаем утечки 0.001
    
    //std::cout << state.cavities_count() << std::endl;

    auto A_func = std::function<State<TCH_State>(const TCH_State&)>{[](const TCH_State& state){
        State<TCH_State> res;
        for (int i = 0; i < state.cavities_count(); i++) {
            int ph = state.get_qudit(0, i);
            if (ph != 0) {
                res += set_qudit(state, ph - 1, 0, i) * state.get_leak_gamma(i);
            }
        }
        return res;
    }};
    auto A = Operator<TCH_State>(A_func);
    std::vector<std::pair<double, Operator<TCH_State>>> dec;
    dec.emplace_back(1, A);
    State<TCH_State> init_state(state);
    //H_TCH H(init_state, dec);
    H_TCH H(init_state);

    //show_basis(H.get_basis());

    auto time_vec = linspace(0, 1000, 2000);
    auto probs = quantum_master_equation(init_state.fit_to_basis_state(H.get_basis()), H, time_vec);

    return probs[probs.n() - 1][time_vec.size() - 1];
}

template<std::size_t size>
void calculate_conductivity(const std::vector<std::vector<bool>>& graph, int argc, char *argv[], int step, MPI_File *fout) {
    using namespace QComputations;
    int rank, world_size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    size_t start_col, count;

    make_rank_map(size, rank, world_size, start_col, count);

    for (std::size_t start = start_col; start < start_col + count; ++start) {
        std::cout << start << std::endl;
        for (std::size_t finish = 0; finish < size; ++finish) {
            if (start != finish) {
                double p = get_conductivity<size>(graph, start, finish);
                WRITE_result(fout, step, start, finish, p, size);
            } else if (start == finish) {
                WRITE_result(fout, step, start, finish, -1, graph.size());
            }
        }
    }
}

int main(int argc, char *argv[]) {
    const int size = 20;

    int rank, world_size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

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

    WRITE_n(&fout, n, size);

    //std::cout << n << std::endl;

    std::vector<std::vector<bool>> g(size, std::vector<bool>(size, false));

    for (int i = 0; i < n; ++i) {
        //std::cout << i << std::endl;
        READ_graph(&fin, i, g);

        calculate_conductivity<size>(g, argc, argv, i, &fout);

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
