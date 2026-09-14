#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array) {
    std::vector<long> result;
    int index = 0;
    while (index < array.size()) {
        result.push_back(array.back());
        array.pop_back();
        index += 2;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)8, (long)8, (long)-4, (long)-9, (long)2, (long)8, (long)-1, (long)8}))) == (std::vector<long>({(long)8, (long)-1, (long)8})));
}
