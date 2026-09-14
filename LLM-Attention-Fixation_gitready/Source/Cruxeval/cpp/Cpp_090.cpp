#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::vector<long>> f(std::vector<std::vector<long>> array) {
    std::vector<std::vector<long>> return_arr;
    for (const auto& a : array) {
        return_arr.push_back(a);
    }
    return return_arr;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::vector<long>>({(std::vector<long>)std::vector<long>({(long)1, (long)2, (long)3}), (std::vector<long>)std::vector<long>(), (std::vector<long>)std::vector<long>({(long)1, (long)2, (long)3})}))) == (std::vector<std::vector<long>>({(std::vector<long>)std::vector<long>({(long)1, (long)2, (long)3}), (std::vector<long>)std::vector<long>(), (std::vector<long>)std::vector<long>({(long)1, (long)2, (long)3})})));
}
