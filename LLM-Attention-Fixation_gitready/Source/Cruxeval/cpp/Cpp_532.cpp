#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::vector<long>> f(long n, std::vector<long> array) {
    std::vector<std::vector<long>> final;
    final.push_back(array);
    for (int i = 0; i < n; i++) {
        std::vector<long> arr = array;
        arr.insert(arr.end(), final.back().begin(), final.back().end());
        final.push_back(arr);
    }
    return final;
}
int main() {
    auto candidate = f;
    assert(candidate((1), (std::vector<long>({(long)1, (long)2, (long)3}))) == (std::vector<std::vector<long>>({(std::vector<long>)std::vector<long>({(long)1, (long)2, (long)3}), (std::vector<long>)std::vector<long>({(long)1, (long)2, (long)3, (long)1, (long)2, (long)3})})));
}
