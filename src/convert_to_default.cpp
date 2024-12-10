#include <iostream>
#include <fstream>
#include <iomanip>

using namespace std;

int main(int argc, char *argv[]) {
    fstream fin;
    size_t width = 15;
    fin.open(argv[1], ios_base::in | ios_base::binary);

    freopen(argv[2], "w", stdout);

    int n;
    fin.read((char *)&n, 4);
    cout << std::setw(width) << n << "\n";

    int size;
    fin.read((char *)&size, 4);
    cout << std::setw(width) << size << "\n";

    for (int i = 0; i < n; ++i) {
        for (int d1 = 0; d1 < size; ++d1) {
            for (int d2 = 0; d2 < size; ++d2) {
                double v;
                fin.read((char *)&v, sizeof(double));
                cout << std::setw(width) << v << " ";
            }
            cout << "\n";
        }

        cout << "\n";
    }

    fin.close();
    fclose(stdout);

    return 0;
}

