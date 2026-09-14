#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array, long num) {
    bool reverse = false;
    if (num < 0) {
        reverse = true;
        num *= -1;
    }
    std::reverse(array.begin(), array.end());
    array.insert(array.end(), array.begin(), array.end() - array.size() * num);

    if (reverse) {
        std::reverse(array.begin(), array.end());
    }
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2})), (1)) == (std::vector<long>({(long)2, (long)1})));
}
