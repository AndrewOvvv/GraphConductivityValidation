#include "graph.hpp"
#include "QComputations_CPU_CLUSTER.hpp"
#include <cstddef>
#include <vector>

template<std::size_t size>
double get_conductivity(const graph::Graph<size>& graph, std::size_t start, std::size_t finish) {
    using namespace QComputations;
    MPI_Init(&argc, &argv);
    int rank, world_size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    size_t cavity_counts = size; // число полостей
    std::vector<size_t> grid_atoms; // задаёт количество частиц в каждой полости, у нас везде будут 0
    for (size_t i = 0; i < cavity_counts; i++){
        grid_atoms.emplace_back(0);
    }

    std::pair<double, double> gamma = std::make_pair(0.01, 1); // амплитуда с длиной волновода перехода из полости в полости
    std::pair<double, double> pair_zero = std::make_pair(0, 0); // нет перехода
                                                                //
    Matrix<std::pair<double, double>> waveguides_parametrs(graph.convert_to_system(gamma, pair_zero)); // матрица параметров
    
    State state(grid_atoms);
    state.set_waveguide(waveguides_parametrs);

    state.set_n(1, start); // в 0 полость помещаем 1 фотон
    state.set_leak_for_cavity(finish, 0.001); // для 2 полости делаем утечки 0.001

    int ctxt;
    mpi::init_grid(ctxt); // делаем сетку процессов
    BLOCKED_H_TCH H(ctxt, state);

    if (rank == 0) show_basis(H.get_basis());

    H.show();

    std::vector<COMPLEX> init_state(H.get_basis().size(), 0);
    init_state[state.get_index(H.get_basis())] = COMPLEX(1, 0);
    auto time_vec = linspace(0, 100000, 100000);

    auto probs = Evolution::quantum_master_equation(init_state, H, time_vec);

    state.set_n(0, 0);
    auto global_row = state.get_index(H.get_basis());
    auto zero_state_probs = blocked_matrix_get_row(probs.ctxt(), probs, global_row);

    /*
    //probs.show();

    if (rank == 0) {
        matplotlib::make_figure(1920, 1080);
    }

    matplotlib::probs_to_plot(probs, time_vec, H.get_basis());
    if (rank == 0) {
        matplotlib::grid();
        matplotlib::show();
    }
    */
    MPI_Finalize();
    return zero_state_probs[finish]; // TODO
}

template<std::size_t size>
std::vector<double> calculate_conductivity(const graph::Graph<size>& graph) {
    std::vector<double> result;
    for (std::size_t start = 0; start < size; ++start) {
        for (std::size_t finish = 0; finish < size; ++finish) {
            if (start != finish) {
                result.push_back(get_conductivity(graph, start, finish));
            }
        }
    }
    return result;
}

int main(int argc, char *argv[]) {
    const int size = 5;
    graph::Graph<size> graph;
    
    int n; std::cin >> n;
    std::cout << n << std::endl;
    for (int i = 0; i < n; ++i) {
        std::cin >> graph; 
        auto result = calculate_conductivity(graph);
        for (int i = 0; i < int(result.size()); ++i) {
            std::cout << result[i] << " ";
        }
        std::cout << std::endl;
    }
    return 0;
}
