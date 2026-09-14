#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    for (int i = nums.size()-1; i >= 0; i--) {
        if (nums[i] % 2 == 1) {
            nums.insert(nums.begin() + i + 1, nums[i]);
        }
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)2, (long)3, (long)4, (long)6, (long)-2}))) == (std::vector<long>({(long)2, (long)3, (long)3, (long)4, (long)6, (long)-2})));
}
