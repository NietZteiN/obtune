#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int n = nums.size();
    for (int i = 0; i < n; ++i) {
        if (nums[i] % 3 == 0) {
            nums.push_back(nums[i]);
        }
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)3}))) == (std::vector<long>({(long)1, (long)3, (long)3})));
}
