#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    size_t original_size = nums.size();
    for (size_t i = 0; i < original_size; ++i) {
        nums.insert(nums.begin() + i, nums[i]);
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)3, (long)-1, (long)1, (long)-2, (long)6}))) == (std::vector<long>({(long)1, (long)1, (long)1, (long)1, (long)1, (long)1, (long)1, (long)3, (long)-1, (long)1, (long)-2, (long)6})));
}
