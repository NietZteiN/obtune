#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long n) {
    int pos = nums.size() - 1;
    for (int i = -nums.size(); i < 0; i++) {
        nums.insert(nums.begin() + pos, nums[i]);
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>()), (14)) == (std::vector<long>()));
}
