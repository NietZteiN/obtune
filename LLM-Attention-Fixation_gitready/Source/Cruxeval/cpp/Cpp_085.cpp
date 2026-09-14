#include<bits/stdc++.h>

std::vector<float> f(long n) {
    std::map<long, float> values = {{0, 3}, {1, 4.5}, {2, 0}};
    std::map<long, long> res;
    for (auto const &pair : values) {
        if (pair.first % n != 2) {
            res[pair.second] = n / 2;
        }
    }
    std::vector<float> result;
    for (auto const &pair : res) {
        result.push_back(pair.first);
    }
    std::sort(result.begin(), result.end());
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((12)) == (std::vector<float>({(long)3, (long)4.5f})));
}
