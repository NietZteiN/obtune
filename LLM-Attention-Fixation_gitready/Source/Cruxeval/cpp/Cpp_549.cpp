#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::vector<long>> f(std::vector<std::vector<long>> matrix) {
    std::reverse(matrix.begin(), matrix.end());
    std::vector<std::vector<long>> result;
    for (auto& primary : matrix) {
        std::sort(primary.rbegin(), primary.rend());
        result.push_back(primary);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::vector<long>>({(std::vector<long>)std::vector<long>({(long)1, (long)1, (long)1, (long)1})}))) == (std::vector<std::vector<long>>({(std::vector<long>)std::vector<long>({(long)1, (long)1, (long)1, (long)1})})));
}
