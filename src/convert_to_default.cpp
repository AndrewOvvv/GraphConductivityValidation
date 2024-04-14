#include <iostream>
#include <fstream>

using namespace std;

int main(int argc, char *argv[]) {
    fstream fin;
    fin.open(argv[1], ios_base::in | ios_base::binary);

    freopen(argv[2], "w", stdout);

    int n;
    fin.read((char *)&n, 4);
    cout << n << "\n";

    for (int i = 0; i < n; ++i) {
        int size;
        fin.read((char *)&size, 4);
        cout << size << "\n";
        for (int d1 = 0; d1 < size; ++d1) {
            for (int d2 = 0; d2 < size; ++d2) {
                int v;
                fin.read((char *)&v, 4);
                cout << v;
            }
            cout << "\n";
        }
    }

    fin.close();
    fclose(stdout);

    return 0;
}
