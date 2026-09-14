#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array, long index, long value) {
    array.insert(array.begin(), index + 1);
    if (value >= 1) {
        array.insert(array.begin() + index, value);
    }
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)2})), (0), (2)) == (std::vector<long>({(long)2, (long)1, (long)2})));
}
