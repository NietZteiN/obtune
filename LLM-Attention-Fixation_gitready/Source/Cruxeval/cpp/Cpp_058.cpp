#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int count = nums.size();
    for (int i = 0; i < count; i++) {
        nums.push_back(nums[i % 2]);
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-1, (long)0, (long)0, (long)1, (long)1}))) == (std::vector<long>({(long)-1, (long)0, (long)0, (long)1, (long)1, (long)-1, (long)0, (long)-1, (long)0, (long)-1})));
}
