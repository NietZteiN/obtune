#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array, long elem) {
    int k = 0;
    std::vector<long> l = array;
    for (int i : l) {
        if (i > elem) {
            array.insert(array.begin() + k, elem);
            break;
        }
        k++;
    }
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)5, (long)4, (long)3, (long)2, (long)1, (long)0})), (3)) == (std::vector<long>({(long)3, (long)5, (long)4, (long)3, (long)2, (long)1, (long)0})));
}
