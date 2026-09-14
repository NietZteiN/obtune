#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array) {
    std::vector<long> new_array = array;
    std::reverse(new_array.begin(), new_array.end());
    std::vector<long> result;
    for (auto x : new_array) {
        result.push_back(x * x);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)1}))) == (std::vector<long>({(long)1, (long)4, (long)1})));
}
