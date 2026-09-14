#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array, std::vector<long> values) {
    std::reverse(array.begin(), array.end());
    for (int value : values) {
        array.insert(array.begin() + array.size() / 2, value);
    }
    std::reverse(array.begin(), array.end());
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)58})), (std::vector<long>({(long)21, (long)92}))) == (std::vector<long>({(long)58, (long)92, (long)21})));
}
