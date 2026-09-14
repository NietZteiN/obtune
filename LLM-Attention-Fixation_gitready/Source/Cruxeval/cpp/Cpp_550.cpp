#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int size = nums.size();
    for (int i = 0; i < size; i++) {
        nums.insert(nums.begin() + i, nums[i]);
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)4}))) == (std::vector<long>({(long)1, (long)1, (long)1, (long)1, (long)2, (long)4})));
}
