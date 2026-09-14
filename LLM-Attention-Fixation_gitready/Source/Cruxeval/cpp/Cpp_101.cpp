#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array, int i_num, long elem) {
    array.insert(array.begin() + i_num, elem);
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-4, (long)1, (long)0})), (1), (4)) == (std::vector<long>({(long)-4, (long)4, (long)1, (long)0})));
}
