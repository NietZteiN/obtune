#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array, long ind, long elem) {
    if (ind < 0) {
        array.insert(array.begin() - 5, elem);
    }
    else if (ind > array.size()) {
        array.insert(array.end(), elem);
    }
    else {
        array.insert(array.begin() + ind + 1, elem);
    }

    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)5, (long)8, (long)2, (long)0, (long)3})), (2), (7)) == (std::vector<long>({(long)1, (long)5, (long)8, (long)7, (long)2, (long)0, (long)3})));
}
