#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long sort_count) {
    std::sort(nums.begin(), nums.end());
    return std::vector<long>(nums.begin(), nums.begin() + sort_count);
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)2, (long)3, (long)4, (long)5})), (1)) == (std::vector<long>({(long)1})));
}
