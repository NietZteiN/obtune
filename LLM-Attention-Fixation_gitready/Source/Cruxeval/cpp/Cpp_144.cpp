#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::vector<long>> f(std::vector<std::vector<long>> vectors) {
    std::vector<std::vector<long>> sorted_vecs;
    for(auto& vec : vectors) {
        std::sort(vec.begin(), vec.end());
        sorted_vecs.push_back(vec);
    }
    return sorted_vecs;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::vector<long>>())) == (std::vector<std::vector<long>>()));
}
