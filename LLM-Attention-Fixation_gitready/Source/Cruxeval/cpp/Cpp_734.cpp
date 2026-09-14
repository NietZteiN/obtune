#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    for (int i = nums.size() - 1; i >= 0; i--) {
        if (nums[i] % 2 == 0) {
            nums.erase(nums.begin() + i);
        }
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)5, (long)3, (long)3, (long)7}))) == (std::vector<long>({(long)5, (long)3, (long)3, (long)7})));
}
