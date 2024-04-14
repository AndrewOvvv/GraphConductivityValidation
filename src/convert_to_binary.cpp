#include <iostream>
#include <fstream>

using namespace std;

int main(int argc, char *argv[]) {
    freopen(argv[1], "r", stdin);

    fstream fout;
    fout.open(argv[2], ios_base::out | ios_base::binary);

    int z = 0, o = 1;
    int n; cin >> n;
    fout.write((char *)&n, 4);
    //fout << n;

    for (int i = 0; i < n; ++i) {
        int size; cin >> size;
        fout.write((char *)&size, 4);
        //fout << size;
        for (int d1 = 0; d1 < size; ++d1) {
            for (int d2 = 0; d2 < size; ++d2) {
                char c; cin >> c;
                if (c == '0') {
                    fout.write((char *)&z, 4);
                    //fout << 0;
                } else {
                    fout.write((char *)&o, 4);
                    //fout << 1;
                }
            }
        }
    }

    fclose(stdin);
    fout.close();

    return 0;
}
