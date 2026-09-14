#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array, long L) {
    if (L <= 0) {
        return array;
    }
    if (array.size() < L) {
        std::vector<long> temp(array.end() - std::min((long)array.size(), L), array.end());
        array.insert(array.end(), temp.begin(), temp.end());
    }
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3})), (4)) == (std::vector<long>({(long)1, (long)2, (long)3, (long)1, (long)2, (long)3})));
}
