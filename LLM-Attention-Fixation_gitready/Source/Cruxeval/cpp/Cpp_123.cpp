#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array, long elem) {
    for (int idx = 0; idx < array.size(); idx++) {
        if (array[idx] > elem && array[idx - 1] < elem) {
            array.insert(array.begin() + idx, elem);
        }
    }
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3, (long)5, (long)8})), (6)) == (std::vector<long>({(long)1, (long)2, (long)3, (long)5, (long)6, (long)8})));
}
