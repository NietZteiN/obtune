#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    size_t middle = nums.size() / 2;
    std::vector<long> result(nums.begin() + middle, nums.end());
    result.insert(result.end(), nums.begin(), nums.begin() + middle);
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)1, (long)1}))) == (std::vector<long>({(long)1, (long)1, (long)1})));
}
